import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, DollarSign, ShoppingBag, TrendingUp, Plus, Edit, Trash2, X, Save } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const categories = [
  { id: 1, name: 'Fresh Produce' },
  { id: 2, name: 'Grains & Flours' },
  { id: 3, name: 'Condiments & Seasonings' },
  { id: 4, name: 'Frozen Foods & Meats' },
  { id: 5, name: 'Snacks & Confectionery' },
  { id: 6, name: 'Drinks & Beverages' },
  { id: 7, name: 'Dried & Preserved Foods' },
  { id: 8, name: 'Beauty & Household' },
];

const VendorDashboard = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  
  const [productForm, setProductForm] = useState({
    name: '',
    brand: '',
    description: '',
    price: '',
    originalPrice: '',
    image: '',
    category: '',
    categoryId: '',
    stock: '',
    weight: '',
    featured: false
  });

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (user?.role !== 'vendor') {
      toast.error('You must be a vendor to access this page');
      navigate('/');
      return;
    }
    
    fetchDashboardData();
  }, [isAuthenticated, user]);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('afroToken');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [productsRes, statsRes] = await Promise.all([
        axios.get(`${API}/vendor/products`, { headers }),
        axios.get(`${API}/vendor/dashboard/stats`, { headers })
      ]);
      
      setProducts(productsRes.data);
      setStats(statsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProductForm({ ...productForm, [name]: value });
  };

  const handleCategoryChange = (value) => {
    const selectedCat = categories.find(c => c.name === value);
    setProductForm({
      ...productForm,
      category: value,
      categoryId: selectedCat?.id || ''
    });
  };

  const resetForm = () => {
    setProductForm({
      name: '',
      brand: '',
      description: '',
      price: '',
      originalPrice: '',
      image: '',
      category: '',
      categoryId: '',
      stock: '',
      weight: '',
      featured: false
    });
    setEditingProduct(null);
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('afroToken');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(`${API}/vendor/products`, productForm, { headers });
      
      toast.success('Product added successfully!');
      setShowAddProduct(false);
      resetForm();
      fetchDashboardData();
    } catch (error) {
      console.error('Error adding product:', error);
      toast.error(error.response?.data?.detail || 'Failed to add product');
    }
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setProductForm({
      name: product.name,
      brand: product.brand,
      description: product.description || '',
      price: product.price,
      originalPrice: product.originalPrice || '',
      image: product.image,
      category: product.category,
      categoryId: product.categoryId || categories.find(c => c.name === product.category)?.id || '',
      stock: product.stock,
      weight: product.weight || '',
      featured: product.featured
    });
    setShowAddProduct(true);
  };

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('afroToken');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.put(`${API}/vendor/products/${editingProduct.id}`, productForm, { headers });
      
      toast.success('Product updated successfully!');
      setShowAddProduct(false);
      resetForm();
      fetchDashboardData();
    } catch (error) {
      console.error('Error updating product:', error);
      toast.error('Failed to update product');
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    
    try {
      const token = localStorage.getItem('afroToken');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.delete(`${API}/vendor/products/${productId}`, { headers });
      
      toast.success('Product deleted successfully!');
      fetchDashboardData();
    } catch (error) {
      console.error('Error deleting product:', error);
      toast.error('Failed to delete product');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Vendor Dashboard</h1>
            <p className="text-gray-600 mt-2">Welcome back, {user?.name}!</p>
          </div>
          <Dialog open={showAddProduct} onOpenChange={(open) => {
            setShowAddProduct(open);
            if (!open) resetForm();
          }}>
            <DialogTrigger asChild>
              <Button className="bg-emerald-600 hover:bg-emerald-700">
                <Plus className="h-4 w-4 mr-2" />
                Add New Product
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{editingProduct ? 'Edit Product' : 'Add New Product'}</DialogTitle>
              </DialogHeader>
              <form onSubmit={editingProduct ? handleUpdateProduct : handleAddProduct} className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <Label>Product Name *</Label>
                    <Input
                      name="name"
                      value={productForm.name}
                      onChange={handleInputChange}
                      placeholder="e.g., Ayoola Poundo Yam Flour"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label>Brand *</Label>
                    <Input
                      name="brand"
                      value={productForm.brand}
                      onChange={handleInputChange}
                      placeholder="e.g., Ayoola"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label>Category *</Label>
                    <Select value={productForm.category} onValueChange={handleCategoryChange} required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map(cat => (
                          <SelectItem key={cat.id} value={cat.name}>{cat.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label>Price (£) *</Label>
                    <Input
                      name="price"
                      type="number"
                      step="0.01"
                      value={productForm.price}
                      onChange={handleInputChange}
                      placeholder="8.99"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label>Original Price (£) - Optional</Label>
                    <Input
                      name="originalPrice"
                      type="number"
                      step="0.01"
                      value={productForm.originalPrice}
                      onChange={handleInputChange}
                      placeholder="10.99"
                    />
                  </div>
                  
                  <div>
                    <Label>Stock Quantity *</Label>
                    <Input
                      name="stock"
                      type="number"
                      value={productForm.stock}
                      onChange={handleInputChange}
                      placeholder="50"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label>Weight/Size *</Label>
                    <Input
                      name="weight"
                      value={productForm.weight}
                      onChange={handleInputChange}
                      placeholder="e.g., 1.5kg, 500g"
                      required
                    />
                  </div>
                  
                  <div className="col-span-2">
                    <Label>Image URL *</Label>
                    <Input
                      name="image"
                      type="url"
                      value={productForm.image}
                      onChange={handleInputChange}
                      placeholder="https://example.com/image.jpg"
                      required
                    />
                  </div>
                  
                  <div className="col-span-2">
                    <Label>Description *</Label>
                    <Textarea
                      name="description"
                      value={productForm.description}
                      onChange={handleInputChange}
                      placeholder="Describe your product..."
                      rows={3}
                      required
                    />
                  </div>
                  
                  <div className="col-span-2 flex items-center space-x-2">
                    <Checkbox
                      id="featured"
                      checked={productForm.featured}
                      onCheckedChange={(checked) => setProductForm({ ...productForm, featured: checked })}
                    />
                    <Label htmlFor="featured" className="cursor-pointer">
                      Mark as Featured Product
                    </Label>
                  </div>
                </div>
                
                <div className="flex gap-3 pt-4">
                  <Button type="submit" className="flex-1 bg-emerald-600 hover:bg-emerald-700">
                    <Save className="h-4 w-4 mr-2" />
                    {editingProduct ? 'Update Product' : 'Add Product'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowAddProduct(false);
                      resetForm();
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Sales</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.totalSales || 0}</p>
                </div>
                <div className="bg-emerald-100 p-3 rounded-full">
                  <ShoppingBag className="h-6 w-6 text-emerald-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Revenue</p>
                  <p className="text-3xl font-bold text-gray-900">£{(stats.revenue || 0).toFixed(2)}</p>
                </div>
                <div className="bg-orange-100 p-3 rounded-full">
                  <DollarSign className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Active Products</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.totalProducts || 0}</p>
                </div>
                <div className="bg-blue-100 p-3 rounded-full">
                  <Package className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Rating</p>
                  <p className="text-3xl font-bold text-gray-900">{(stats.rating || 0).toFixed(1)} ⭐</p>
                </div>
                <div className="bg-purple-100 p-3 rounded-full">
                  <TrendingUp className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Card>
          <CardContent className="p-6">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="products">My Products ({products.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="overview">
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold">Quick Stats</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card className="bg-gradient-to-br from-emerald-50 to-green-50">
                      <CardContent className="pt-6">
                        <h4 className="font-semibold text-gray-900 mb-2">📦 Products</h4>
                        <p className="text-sm text-gray-600">You have {products.length} active products listed on the marketplace.</p>
                      </CardContent>
                    </Card>
                    
                    <Card className="bg-gradient-to-br from-orange-50 to-yellow-50">
                      <CardContent className="pt-6">
                        <h4 className="font-semibold text-gray-900 mb-2">💰 Commission</h4>
                        <p className="text-sm text-gray-600">Platform commission is £1 per item sold. Your earnings are maximized!</p>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="products">
                <div className="space-y-4">
                  {products.length === 0 ? (
                    <div className="text-center py-12">
                      <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">No Products Yet</h3>
                      <p className="text-gray-600 mb-6">Start adding products to your store!</p>
                      <Button onClick={() => setShowAddProduct(true)} className="bg-emerald-600 hover:bg-emerald-700">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Your First Product
                      </Button>
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Product</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Price</TableHead>
                          <TableHead>Stock</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {products.map((product) => (
                          <TableRow key={product.id}>
                            <TableCell>
                              <div className="flex items-center gap-3">
                                <img
                                  src={product.image}
                                  alt={product.name}
                                  className="w-12 h-12 object-cover rounded"
                                />
                                <div>
                                  <p className="font-medium">{product.name}</p>
                                  <p className="text-sm text-gray-600">{product.brand}</p>
                                </div>
                              </div>
                            </TableCell>
                            <TableCell>{product.category}</TableCell>
                            <TableCell>
                              <div>
                                <span className="font-semibold">£{product.price?.toFixed(2)}</span>
                                {product.originalPrice && (
                                  <span className="text-sm text-gray-500 line-through ml-2">
                                    £{product.originalPrice?.toFixed(2)}
                                  </span>
                                )}
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge variant={product.stock > 20 ? 'default' : 'destructive'}>
                                {product.stock} units
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge className={product.inStock ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}>
                                {product.inStock ? 'In Stock' : 'Out of Stock'}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex gap-2 justify-end">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleEditProduct(product)}
                                >
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                  onClick={() => handleDeleteProduct(product.id)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default VendorDashboard;
