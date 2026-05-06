// Synthetic PII per spec §8 binding rules.
// All identifiers are deliberately fictional and fail public-registry lookup.

export const extractionRich = {
  fields: {
    invoice_id: "INV-TEST-0001",
    invoice_date: "2026-04-22",
    due_date: "2026-05-22",

    total_amount: 60462,
    net_amount: 56000,
    tax_amount: 1600,
    freight_charge: 2862,
    currency: "USD",

    exporter_name: "Acme Test Exports SAS",
    exporter_address: "Calle Test #1-2, Test City, Country",
    exporter_email: "ap@example.org",
    exporter_phone: "+1 555 555 0100",
    exporter_tax_id: "NIT 000.000.000-0",

    importer_name: "Liquidation Test Co",
    importer_address: "1 Test Way, Doral, FL 33172",
    importer_email: "ops@example.com",
    importer_tax_id: "EIN 00-0000000",

    shipping_recipient: "Test Warehouse #0",
    shipping_address: "1 Test Way Bay 0, Doral, FL 33172",

    purchase_order: "PO-TEST-2026-0001",
    payment_terms: "Net 30",
  },
  line_items: [
    { description: "Test Item A", quantity: 120, unit_price: 385.0, amount: 46200.0 },
    { description: "Test Item B", quantity: 40, unit_price: 245.0, amount: 9800.0 },
    { description: "Test Item C", quantity: 500, unit_price: 3.2, amount: 1600.0 },
    { description: "Test Item D — handling", quantity: null, unit_price: null, amount: 2862.0 },
  ],
};
