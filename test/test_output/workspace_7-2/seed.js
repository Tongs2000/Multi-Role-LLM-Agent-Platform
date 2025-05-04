const mongoose = require('mongoose');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Filter Preset Schema
const FilterPresetSchema = new mongoose.Schema({
  name: String,
  config: Object,
});

const FilterPreset = mongoose.model('FilterPreset', FilterPresetSchema);

// Sample presets
const presets = [
  {
    name: 'grayscale',
    config: { grayscale: true },
  },
  {
    name: 'sepia',
    config: { sepia: true },
  },
  {
    name: 'vintage',
    config: { brightness: 0.8, saturation: 0.5, hue: 120 },
  },
];

// Seed the database
async function seed() {
  try {
    await FilterPreset.deleteMany({}); // Clear existing presets
    await FilterPreset.insertMany(presets); // Insert new presets
    console.log('Database seeded successfully!');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
}

seed();