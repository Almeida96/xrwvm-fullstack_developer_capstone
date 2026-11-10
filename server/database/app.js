const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('node:path');
const app = express()
const port = process.env.PORT || 3030;

app.use(express.json({ limit: "64kb" }));
app.use(express.urlencoded({extended: false, limit: "64kb"}));

const reviews_data = JSON.parse(fs.readFileSync(path.join(__dirname, "data/reviews.json"), 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync(path.join(__dirname, "data/dealerships.json"), 'utf8'));

const Reviews = require('./review');
const Dealerships = require('./dealership');
const Counter = mongoose.model('review_counter', new mongoose.Schema({_id: String, value: Number}));

async function initialize() {
  await mongoose.connect(process.env.MONGO_URI || "mongodb://127.0.0.1:27017/", {dbName: "dealershipsDB"});
  for (const [Model, rows] of [[Reviews, reviews_data.reviews], [Dealerships, dealerships_data.dealerships]]) {
    await Model.bulkWrite(rows.map(row => ({updateOne: {filter: {id: row.id}, update: {$setOnInsert: row}, upsert: true}})));
  }
  const last = await Reviews.findOne().sort({id: -1});
  await Counter.updateOne({_id: "review"}, {$max: {value: last?.id || 0}}, {upsert: true});
}

// Express route to home
app.get('/', async (req, res) => {
    res.send("Welcome to the Mongoose API")
});

// Express route to fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({dealership: req.params.id});
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    const dealers = await Dealerships.find().sort({ id: 1 });
    res.json(dealers);
  } catch (error) {
    console.error('Error fetching dealerships:', error);
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

// Express route to fetch Dealers by a particular state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const state = req.params.state.trim();
    // "All" resets the state filter from the React dealerships dropdown.
    const filter = state.toLowerCase() === 'all' ? {} : { state };
    const dealers = await Dealerships.find(filter).sort({ id: 1 });
    return res.json(dealers);
  } catch (error) {
    console.error('Error fetching dealerships by state:', error);
    return res.status(500).json({ error: 'Error fetching dealerships by state' });
  }
});

// Express route to fetch dealer by a particular id
app.get('/fetchDealer/:id', async (req, res) => {
  const dealerId = Number(req.params.id);
  if (!Number.isInteger(dealerId) || dealerId < 1) {
    return res.status(400).json({ error: 'Invalid dealership ID' });
  }
  try {
    // Return an array so the Django/React dealership-detail page can consume it.
    const dealers = await Dealerships.find({ id: dealerId });
    if (dealers.length === 0) {
      return res.status(404).json({ error: 'Dealership not found' });
    }
    return res.json(dealers);
  } catch (error) {
    console.error('Error fetching dealership by ID:', error);
    return res.status(500).json({ error: 'Error fetching dealership' });
  }
});

//Express route to insert review
app.post('/insert_review', async (req, res) => {
  const data = req.body;
  if (!data || !Number.isSafeInteger(data.dealership) || data.dealership < 1 ||
      typeof data.review !== 'string' || !data.review.trim() || data.review.length > 5000 ||
      typeof data.name !== 'string' || !data.name.trim() || data.name.length > 300 ||
      typeof data.purchase !== 'boolean' || !Number.isInteger(data.car_year) ||
      data.car_year < 1900 || data.car_year > 2100 ||
      !['car_make', 'car_model', 'purchase_date'].every(key => typeof data[key] === 'string' && data[key].length <= 100)) {
    return res.status(400).json({error: 'Invalid review input'});
  }
  try {
    if (!await Dealerships.exists({id: data.dealership})) return res.status(404).json({error: 'Dealership not found'});
    const counter = await Counter.findOneAndUpdate({_id: 'review'}, {$inc: {value: 1}}, {new: true});
    const saved = await Reviews.create({...data, id: counter.value});
    return res.status(201).json(saved);
  } catch (error) {
    return res.status(500).json({error: 'Unable to save review'});
  }
});
app.use((error, req, res, next) => {
  if (error.type === 'entity.parse.failed') return res.status(400).json({error: 'Invalid JSON'});
  if (error.type === 'entity.too.large') return res.status(413).json({error: 'Request too large'});
  return res.status(500).json({error: 'Service error'});
});
initialize().then(() => {
  app.listen(port, process.env.HOST || '127.0.0.1', () => console.log(`Dealership data service listening on ${port}`));
}).catch(error => { console.error('Cannot initialize dealership database'); process.exitCode = 1; mongoose.disconnect(); });
