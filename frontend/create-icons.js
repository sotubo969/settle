const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

async function createIcons() {
  const logoPath = path.join(__dirname, 'public', 'dammy-logo.jpg');
  const outputDir = path.join(__dirname, 'public');
  
  console.log('📸 Creating app icons from logo...');
  
  // Icon sizes needed
  const sizes = [
    { size: 192, name: 'logo192.png' },
    { size: 512, name: 'logo512.png' },
    { size: 48, name: 'logo48.png' },
    { size: 72, name: 'logo72.png' },
    { size: 96, name: 'logo96.png' },
    { size: 144, name: 'logo144.png' },
    { size: 1024, name: 'logo1024.png' }
  ];
  
  try {
    for (const { size, name } of sizes) {
      await sharp(logoPath)
        .resize(size, size, {
          fit: 'contain',
          background: { r: 255, g: 255, b: 255, alpha: 1 }
        })
        .png()
        .toFile(path.join(outputDir, name));
      
      console.log(`✅ Created ${name} (${size}x${size})`);
    }
    
    console.log('\n🎉 All icons created successfully!');
    console.log('📁 Location: /app/frontend/public/');
    
  } catch (error) {
    console.error('❌ Error creating icons:', error);
    process.exit(1);
  }
}

createIcons();
