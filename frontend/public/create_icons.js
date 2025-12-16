const fs = require('fs');
const { createCanvas } = require('canvas');

// Function to create an icon
function createIcon(size, filename) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');
  
  // Draw green background
  ctx.fillStyle = '#059669';
  ctx.fillRect(0, 0, size, size);
  
  // Draw white "AM" text
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${size * 0.4}px Arial`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('AM', size / 2, size / 2);
  
  // Save to file
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(filename, buffer);
  console.log(`✅ Created ${filename}`);
}

// Check if canvas is available
try {
  createIcon(192, 'logo192.png');
  createIcon(512, 'logo512.png');
} catch (error) {
  console.log('Canvas not available, using alternative method');
  process.exit(1);
}
