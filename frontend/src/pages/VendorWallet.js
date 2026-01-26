import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Wallet, Plus, CreditCard, ArrowUpCircle, ArrowDownCircle, 
  RefreshCw, Settings, History, Loader2, AlertCircle, CheckCircle,
  TrendingUp, Clock, Zap
} from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// Helper to get auth token
const getAuthToken = () => {
  return localStorage.getItem('afroToken') || localStorage.getItem('token');
};

// Top-up amounts
const TOPUP_OPTIONS = [
  { amount: 10, label: '£10', popular: false },
  { amount: 25, label: '£25', popular: true },
  { amount: 50, label: '£50', popular: false },
  { amount: 100, label: '£100', popular: false },
  { amount: 250, label: '£250', popular: false },
  { amount: 500, label: '£500', popular: false },
];

// Payment Form Component
const TopUpPaymentForm = ({ amount, onSuccess, onCancel }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handlePayment = async (e) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setLoading(true);
    setErrorMessage('');
    
    try {
      const token = getAuthToken();
      
      if (!token) {
        toast.error('Please log in to continue');
        return;
      }
      
      // Create payment intent for wallet top-up
      const { data: paymentData } = await axios.post(
        `${API}/wallet/topup`,
        { amount },
        { headers: { Authorization: `Bearer ${token}` }}
      );

      if (!paymentData.client_secret) {
        throw new Error('Failed to create payment session');
      }

      // Confirm payment with Stripe
      const { error, paymentIntent } = await stripe.confirmCardPayment(
        paymentData.client_secret,
        {
          payment_method: {
            card: elements.getElement(CardElement),
          }
        }
      );

      if (error) {
        setErrorMessage(error.message);
        toast.error(error.message);
      } else if (paymentIntent.status === 'succeeded') {
        // Confirm top-up on backend
        await axios.post(
          `${API}/wallet/confirm-topup`,
          null,
          { 
            headers: { Authorization: `Bearer ${token}` },
            params: { 
              payment_intent_id: paymentIntent.id,
              amount: amount
            }
          }
        );
        toast.success(`£${amount} added to your wallet!`);
        onSuccess();
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Payment failed';
      setErrorMessage(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handlePayment} className="space-y-4">
      <div className="p-4 bg-green-50 rounded-lg border border-green-200">
        <p className="text-sm text-gray-600 mb-1">Amount to add:</p>
        <p className="text-3xl font-bold text-green-600">£{amount.toFixed(2)}</p>
      </div>
      
      <div className="p-4 border rounded-lg">
        <Label className="mb-2 block">Card Details</Label>
        <CardElement 
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': { color: '#aab7c4' }
              }
            }
          }}
        />
      </div>

      {errorMessage && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {errorMessage}
        </div>
      )}

      <div className="flex gap-2">
        <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
          Cancel
        </Button>
        <Button type="submit" disabled={!stripe || loading} className="flex-1 bg-green-600 hover:bg-green-700">
          {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CreditCard className="w-4 h-4 mr-2" />}
          Pay £{amount.toFixed(2)}
        </Button>
      </div>
    </form>
  );
};

const VendorWallet = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTopUpDialog, setShowTopUpDialog] = useState(false);
  const [selectedAmount, setSelectedAmount] = useState(25);
  const [customAmount, setCustomAmount] = useState('');
  const [showAutoRechargeDialog, setShowAutoRechargeDialog] = useState(false);
  const [autoRechargeSettings, setAutoRechargeSettings] = useState({
    enabled: false,
    threshold: 5,
    amount: 20
  });

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchWalletData();
  }, [user]);

  const fetchWalletData = async () => {
    try {
      const token = getAuthToken();
      
      if (!token) {
        toast.error('Please log in');
        navigate('/login');
        return;
      }
      
      const headers = { Authorization: `Bearer ${token}` };

      const [walletRes, transactionsRes] = await Promise.all([
        axios.get(`${API}/wallet`, { headers }),
        axios.get(`${API}/wallet/transactions`, { headers })
      ]);

      setWallet(walletRes.data.wallet);
      setTransactions(transactionsRes.data.transactions || []);
      
      // Set auto-recharge settings
      if (walletRes.data.wallet) {
        setAutoRechargeSettings({
          enabled: walletRes.data.wallet.auto_recharge_enabled || false,
          threshold: walletRes.data.wallet.auto_recharge_threshold || 5,
          amount: walletRes.data.wallet.auto_recharge_amount || 20
        });
      }
    } catch (error) {
      console.error('Error fetching wallet data:', error);
      if (error.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
        navigate('/login');
      } else if (error.response?.status === 403) {
        toast.error('Only vendors can access the wallet');
      } else {
        toast.error('Failed to load wallet data');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAutoRecharge = async () => {
    try {
      const token = getAuthToken();
      
      await axios.post(
        `${API}/wallet/setup-auto-recharge`,
        autoRechargeSettings,
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast.success('Auto-recharge settings updated');
      setShowAutoRechargeDialog(false);
      fetchWalletData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update settings');
    }
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'topup':
      case 'deposit':
        return <ArrowUpCircle className="w-5 h-5 text-green-500" />;
      case 'ad_spend':
      case 'deduction':
        return <ArrowDownCircle className="w-5 h-5 text-red-500" />;
      case 'auto_recharge':
        return <RefreshCw className="w-5 h-5 text-blue-500" />;
      default:
        return <History className="w-5 h-5 text-gray-500" />;
    }
  };

  const getTransactionBadge = (type) => {
    switch (type) {
      case 'topup':
      case 'deposit':
        return <Badge className="bg-green-100 text-green-800">Top-up</Badge>;
      case 'ad_spend':
        return <Badge className="bg-red-100 text-red-800">Ad Spend</Badge>;
      case 'auto_recharge':
        return <Badge className="bg-blue-100 text-blue-800">Auto Recharge</Badge>;
      case 'refund':
        return <Badge className="bg-purple-100 text-purple-800">Refund</Badge>;
      default:
        return <Badge>{type}</Badge>;
    }
  };

  const getFinalAmount = () => {
    if (customAmount && parseFloat(customAmount) >= 5) {
      return parseFloat(customAmount);
    }
    return selectedAmount;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3" data-testid="wallet-title">
              <Wallet className="w-8 h-8 text-green-600" />
              Advertising Wallet
            </h1>
            <p className="text-gray-600 mt-1">Manage your advertising budget for pay-per-performance ads</p>
          </div>
          
          <Button 
            onClick={() => setShowTopUpDialog(true)} 
            className="bg-green-600 hover:bg-green-700"
            data-testid="topup-wallet-btn"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Funds
          </Button>
        </div>

        {/* Balance Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="md:col-span-2 bg-gradient-to-br from-green-600 to-green-700 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm font-medium">Current Balance</p>
                  <p className="text-4xl font-bold mt-1" data-testid="wallet-balance">
                    £{(wallet?.balance || 0).toFixed(2)}
                  </p>
                  <p className="text-green-200 text-sm mt-2">
                    Available for advertising
                  </p>
                </div>
                <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center">
                  <Wallet className="w-10 h-10" />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-green-500">
                <div>
                  <p className="text-green-200 text-xs">Total Deposited</p>
                  <p className="text-xl font-semibold">£{(wallet?.total_deposited || 0).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-green-200 text-xs">Total Spent</p>
                  <p className="text-xl font-semibold">£{(wallet?.total_spent || 0).toFixed(2)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-500" />
                Auto-Recharge
              </CardTitle>
              <CardDescription>Never run out of ad budget</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Status</span>
                  <Badge className={autoRechargeSettings.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}>
                    {autoRechargeSettings.enabled ? 'Active' : 'Disabled'}
                  </Badge>
                </div>
                
                {autoRechargeSettings.enabled && (
                  <>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Threshold</span>
                      <span className="font-medium">£{autoRechargeSettings.threshold}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Recharge Amount</span>
                      <span className="font-medium">£{autoRechargeSettings.amount}</span>
                    </div>
                  </>
                )}
                
                <Button 
                  variant="outline" 
                  className="w-full mt-2"
                  onClick={() => setShowAutoRechargeDialog(true)}
                  data-testid="configure-auto-recharge-btn"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Configure
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats & Transactions */}
        <Tabs defaultValue="transactions" className="space-y-4">
          <TabsList>
            <TabsTrigger value="transactions" data-testid="transactions-tab">
              <History className="w-4 h-4 mr-2" />
              Transaction History
            </TabsTrigger>
            <TabsTrigger value="usage" data-testid="usage-tab">
              <TrendingUp className="w-4 h-4 mr-2" />
              Usage Summary
            </TabsTrigger>
          </TabsList>

          <TabsContent value="transactions">
            <Card>
              <CardHeader>
                <CardTitle>Recent Transactions</CardTitle>
                <CardDescription>Your wallet activity</CardDescription>
              </CardHeader>
              <CardContent>
                {transactions.length === 0 ? (
                  <div className="text-center py-12">
                    <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions yet</h3>
                    <p className="text-gray-500 mb-4">Add funds to your wallet to start advertising</p>
                    <Button onClick={() => setShowTopUpDialog(true)} className="bg-green-600 hover:bg-green-700">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Your First Funds
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {transactions.map((tx) => (
                      <div 
                        key={tx.id} 
                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                        data-testid={`transaction-${tx.id}`}
                      >
                        <div className="flex items-center gap-4">
                          {getTransactionIcon(tx.type)}
                          <div>
                            <p className="font-medium text-gray-900">{tx.description}</p>
                            <div className="flex items-center gap-2 mt-1">
                              {getTransactionBadge(tx.type)}
                              <span className="text-xs text-gray-500">
                                <Clock className="w-3 h-3 inline mr-1" />
                                {new Date(tx.created_at).toLocaleDateString('en-GB', {
                                  day: 'numeric',
                                  month: 'short',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`font-semibold ${tx.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {tx.amount >= 0 ? '+' : ''}£{Math.abs(tx.amount).toFixed(2)}
                          </p>
                          <p className="text-xs text-gray-500">Balance: £{tx.balance_after.toFixed(2)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="usage">
            <Card>
              <CardHeader>
                <CardTitle>Usage Summary</CardTitle>
                <CardDescription>How your ad budget is being used</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-green-600 font-medium">Total Deposits</p>
                    <p className="text-2xl font-bold text-green-700 mt-1">
                      £{(wallet?.total_deposited || 0).toFixed(2)}
                    </p>
                    <p className="text-xs text-green-600 mt-1">Lifetime deposits</p>
                  </div>
                  
                  <div className="p-4 bg-red-50 rounded-lg">
                    <p className="text-sm text-red-600 font-medium">Total Spent</p>
                    <p className="text-2xl font-bold text-red-700 mt-1">
                      £{(wallet?.total_spent || 0).toFixed(2)}
                    </p>
                    <p className="text-xs text-red-600 mt-1">On advertising</p>
                  </div>
                  
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-600 font-medium">Average Top-up</p>
                    <p className="text-2xl font-bold text-blue-700 mt-1">
                      £{transactions.filter(t => t.type === 'topup' || t.type === 'deposit').length > 0 
                        ? (wallet?.total_deposited / transactions.filter(t => t.type === 'topup' || t.type === 'deposit').length).toFixed(2)
                        : '0.00'}
                    </p>
                    <p className="text-xs text-blue-600 mt-1">Per transaction</p>
                  </div>
                </div>

                <div className="mt-6 p-4 border rounded-lg bg-gray-50">
                  <h4 className="font-medium text-gray-900 mb-3">💡 Tips for Better ROI</h4>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      Set up auto-recharge to ensure your ads never stop running
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      Monitor your ad performance and adjust budgets accordingly
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      Top up in larger amounts to reduce transaction fees
                    </li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Top-Up Dialog */}
      <Dialog open={showTopUpDialog} onOpenChange={setShowTopUpDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Funds to Wallet</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            {/* Amount Selection */}
            <div>
              <Label className="mb-3 block">Select Amount</Label>
              <div className="grid grid-cols-3 gap-2">
                {TOPUP_OPTIONS.map((option) => (
                  <button
                    key={option.amount}
                    onClick={() => {
                      setSelectedAmount(option.amount);
                      setCustomAmount('');
                    }}
                    className={`relative p-3 rounded-lg border-2 transition-all ${
                      selectedAmount === option.amount && !customAmount
                        ? 'border-green-600 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    data-testid={`topup-option-${option.amount}`}
                  >
                    <span className="font-semibold">{option.label}</span>
                    {option.popular && (
                      <span className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs px-1.5 py-0.5 rounded-full font-medium">
                        Popular
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Amount */}
            <div>
              <Label>Or enter custom amount (min £5)</Label>
              <div className="relative mt-1">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">£</span>
                <Input
                  type="number"
                  min="5"
                  step="0.01"
                  value={customAmount}
                  onChange={(e) => {
                    setCustomAmount(e.target.value);
                    if (e.target.value) setSelectedAmount(0);
                  }}
                  placeholder="Enter amount"
                  className="pl-7"
                  data-testid="custom-amount-input"
                />
              </div>
            </div>

            {/* Selected Amount Display */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">You will add:</span>
                <span className="text-2xl font-bold text-green-600">
                  £{getFinalAmount().toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Payment Form */}
          {getFinalAmount() >= 5 && (
            <Elements stripe={stripePromise}>
              <TopUpPaymentForm 
                amount={getFinalAmount()}
                onSuccess={() => {
                  setShowTopUpDialog(false);
                  setCustomAmount('');
                  setSelectedAmount(25);
                  fetchWalletData();
                }}
                onCancel={() => {
                  setShowTopUpDialog(false);
                  setCustomAmount('');
                  setSelectedAmount(25);
                }}
              />
            </Elements>
          )}
        </DialogContent>
      </Dialog>

      {/* Auto-Recharge Dialog */}
      <Dialog open={showAutoRechargeDialog} onOpenChange={setShowAutoRechargeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Configure Auto-Recharge</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base">Enable Auto-Recharge</Label>
                <p className="text-sm text-gray-500">Automatically add funds when balance is low</p>
              </div>
              <Switch
                checked={autoRechargeSettings.enabled}
                onCheckedChange={(checked) => 
                  setAutoRechargeSettings(prev => ({ ...prev, enabled: checked }))
                }
                data-testid="auto-recharge-toggle"
              />
            </div>

            {autoRechargeSettings.enabled && (
              <>
                <div>
                  <Label>Threshold (£)</Label>
                  <p className="text-sm text-gray-500 mb-2">Recharge when balance falls below this amount</p>
                  <Input
                    type="number"
                    min="1"
                    value={autoRechargeSettings.threshold}
                    onChange={(e) => 
                      setAutoRechargeSettings(prev => ({ ...prev, threshold: parseFloat(e.target.value) || 5 }))
                    }
                    data-testid="threshold-input"
                  />
                </div>

                <div>
                  <Label>Recharge Amount (£)</Label>
                  <p className="text-sm text-gray-500 mb-2">Amount to add when auto-recharging</p>
                  <Input
                    type="number"
                    min="5"
                    value={autoRechargeSettings.amount}
                    onChange={(e) => 
                      setAutoRechargeSettings(prev => ({ ...prev, amount: parseFloat(e.target.value) || 20 }))
                    }
                    data-testid="recharge-amount-input"
                  />
                </div>

                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>How it works:</strong> When your balance drops below £{autoRechargeSettings.threshold}, 
                    we'll automatically add £{autoRechargeSettings.amount} using your saved payment method.
                  </p>
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAutoRechargeDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveAutoRecharge} className="bg-green-600 hover:bg-green-700">
              Save Settings
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
};

export default VendorWallet;
