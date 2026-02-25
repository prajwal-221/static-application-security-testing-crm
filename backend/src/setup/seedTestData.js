require('dotenv').config({ path: '.env' });
require('dotenv').config({ path: '.env.local' });
const { generate: uniqueId } = require('shortid');

const mongoose = require('mongoose');
mongoose.connect(process.env.DATABASE);

async function ensureAdmin({ email, name, surname, role, password }) {
  const Admin = require('../models/coreModels/Admin');
  const AdminPassword = require('../models/coreModels/AdminPassword');
  let admin = await Admin.findOne({ email });
  if (!admin) {
    admin = await new Admin({
      email,
      name,
      surname,
      enabled: true,
      role,
    }).save();
    console.log(`Admin created: ${email}`);
  } else {
    console.log(`Admin exists: ${email}`);
  }

  let adminPassword = await AdminPassword.findOne({ user: admin._id });
  if (!adminPassword) {
    const salt = uniqueId();
    const passwordHash = new AdminPassword().generateHash(salt, password);
    await new AdminPassword({
      user: admin._id,
      password: passwordHash,
      emailVerified: true,
      salt,
    }).save();
    console.log(`Admin password created: ${email}`);
  }

  return admin;
}

async function ensurePaymentMode() {
  const PaymentMode = require('../models/appModels/PaymentMode');
  let mode = await PaymentMode.findOne({ isDefault: true });
  if (!mode) {
    mode = await new PaymentMode({
      name: 'Test Payment',
      description: 'Seeded payment mode for scans',
      isDefault: true,
    }).save();
    console.log('Payment mode created');
  }
  return mode;
}

async function ensureClient({ name, email, createdBy }) {
  const Client = require('../models/appModels/Client');
  let client = await Client.findOne({ name, email });
  if (!client) {
    client = await new Client({
      name,
      email,
      phone: '+1-555-0100',
      country: 'US',
      address: '100 Example Ave',
      createdBy,
      assigned: createdBy,
    }).save();
    console.log(`Client created: ${name}`);
  }
  return client;
}

async function ensureQuote({ createdBy, client, number }) {
  const Quote = require('../models/appModels/Quote');
  const year = new Date().getFullYear();
  let quote = await Quote.findOne({ number, year });
  if (!quote) {
    const now = new Date();
    const expiredDate = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000);
    quote = await new Quote({
      createdBy,
      number,
      year,
      date: now,
      expiredDate,
      client,
      items: [
        {
          itemName: 'Discovery Session',
          description: 'Seeded quote line item',
          quantity: 1,
          price: 250,
          total: 250,
        },
      ],
      taxRate: 0,
      subTotal: 250,
      taxTotal: 0,
      total: 250,
      currency: 'USD',
      status: 'sent',
      approved: true,
    }).save();
    console.log('Quote created');
  }
  return quote;
}

async function ensureInvoice({ createdBy, client, number }) {
  const Invoice = require('../models/appModels/Invoice');
  const year = new Date().getFullYear();
  let invoice = await Invoice.findOne({ number, year });
  if (!invoice) {
    const now = new Date();
    const expiredDate = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
    invoice = await new Invoice({
      createdBy,
      number,
      year,
      date: now,
      expiredDate,
      client,
      items: [
        {
          itemName: 'Seeded Service',
          description: 'Invoice line item for scans',
          quantity: 2,
          price: 150,
          total: 300,
        },
      ],
      taxRate: 0,
      subTotal: 300,
      taxTotal: 0,
      total: 300,
      currency: 'USD',
      status: 'sent',
      approved: true,
      paymentStatus: 'unpaid',
    }).save();
    console.log('Invoice created');
  }
  return invoice;
}

async function ensurePayment({ createdBy, client, invoice, paymentMode }) {
  const Payment = require('../models/appModels/Payment');
  let payment = await Payment.findOne({ invoice: invoice._id });
  if (!payment) {
    payment = await new Payment({
      createdBy,
      number: 9001,
      client,
      invoice,
      amount: 150,
      currency: 'USD',
      paymentMode: paymentMode._id,
      ref: 'SEED-PAY-1',
      description: 'Partial payment for seeded invoice',
    }).save();
    console.log('Payment created');
  }
  return payment;
}

async function seed() {
  try {
    const admin = await ensureAdmin({
      email: 'admin@admin.com',
      name: 'IDURAR',
      surname: 'Admin',
      role: 'owner',
      password: 'admin123',
    });

    await ensureAdmin({
      email: 'scanner@idurar.local',
      name: 'Scan',
      surname: 'Account',
      role: 'owner',
      password: 'scanner123',
    });

    await ensureAdmin({
      email: 'auditor@idurar.local',
      name: 'Audit',
      surname: 'Account',
      role: 'owner',
      password: 'auditor123',
    });

    const paymentMode = await ensurePaymentMode();
    const client = await ensureClient({
      name: 'Acme Test Co',
      email: 'billing@acme.test',
      createdBy: admin._id,
    });

    await ensureQuote({ createdBy: admin._id, client: client._id, number: 1001 });
    const invoice = await ensureInvoice({ createdBy: admin._id, client: client._id, number: 2001 });
    await ensurePayment({
      createdBy: admin._id,
      client: client._id,
      invoice,
      paymentMode,
    });

    console.log('Seed test data completed');
    process.exit(0);
  } catch (error) {
    console.log('\nSeed test data failed');
    console.log(error);
    process.exit(1);
  }
}

seed();
