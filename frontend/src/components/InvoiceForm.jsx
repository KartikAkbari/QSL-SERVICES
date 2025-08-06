import { useState } from "react";
import axios from "axios";
import "./InvoiceForm.css";

export default function InvoiceForm() {
  const [form, setForm] = useState({
    clientName: "",
    address: "",
    invoiceNumber: "",
    date: "",
    reference: "",
    services: [
      { description: "", quantity: 1, price: 0 }
    ],
    taxName: "Umsatzsteuer 19%",
    taxRate: 19,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleServiceChange = (idx, e) => {
    const { name, value } = e.target;
    const updated = form.services.map((s, i) =>
      i === idx ? { ...s, [name]: name === "description" ? value : Number(value) } : s
    );
    setForm({ ...form, services: updated });
  };

  const addService = () => {
    setForm({ ...form, services: [...form.services, { description: "", quantity: 1, price: 0 }] });
  };

  const removeService = (idx) => {
    if (form.services.length === 1) return;
    setForm({ ...form, services: form.services.filter((_, i) => i !== idx) });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post("http://localhost:5000/generate-pdf", form, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `Invoice_${form.clientName}.pdf`);
    document.body.appendChild(link);
    link.click();
  };

  return (
    <form onSubmit={handleSubmit} className="invoice-form">
      <h2 className="form-title">Invoice Generator</h2>
      <div className="form-section">
        <h3>Client Information</h3>
        <div className="form-group">
          <label htmlFor="clientName">Client Name</label>
          <input
            id="clientName"
            name="clientName"
            placeholder="Enter client's full name"
            value={form.clientName}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="address">Client Address</label>
          <input
            id="address"
            name="address"
            placeholder="Enter client's address"
            value={form.address}
            onChange={handleChange}
            required
          />
        </div>
      </div>
      <div className="form-section">
        <h3>Invoice Information</h3>
        <div className="form-group">
          <label htmlFor="invoiceNumber">Invoice Number</label>
          <input
            id="invoiceNumber"
            name="invoiceNumber"
            placeholder="e.g. 2025-001"
            value={form.invoiceNumber}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="date">Invoice Date</label>
          <input
            id="date"
            name="date"
            type="date"
            value={form.date}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="reference">Reference</label>
          <input
            id="reference"
            name="reference"
            placeholder="Project or reference"
            value={form.reference}
            onChange={handleChange}
            required
          />
        </div>
      </div>
      <div className="form-section">
        <h3>Service Details</h3>
        {form.services.map((service, idx) => (
          <div className="service-row" key={idx}>
            <div className="form-group service-desc">
              <label>Description</label>
              <input
                name="description"
                placeholder="Describe the service"
                value={service.description}
                onChange={e => handleServiceChange(idx, e)}
                required
              />
            </div>
            <div className="form-group service-qty">
              <label>Quantity</label>
              <input
                name="quantity"
                type="number"
                min="1"
                value={service.quantity}
                onChange={e => handleServiceChange(idx, e)}
                required
              />
            </div>
            <div className="form-group service-price">
              <label>Unit Price (EUR)</label>
              <input
                name="price"
                type="number"
                min="0"
                step="0.01"
                value={service.price}
                onChange={e => handleServiceChange(idx, e)}
                required
              />
            </div>
            <button type="button" className="remove-service-btn" onClick={() => removeService(idx)} disabled={form.services.length === 1}>×</button>
          </div>
        ))}
        <button type="button" className="add-service-btn" onClick={addService}>+ Add Service</button>
      </div>
      <div className="form-section">
        <h3>Tax</h3>
        <div className="form-group-inline">
          <div className="form-group">
            <label htmlFor="taxName">Tax Name</label>
            <input
              id="taxName"
              name="taxName"
              placeholder="e.g. Umsatzsteuer 19%"
              value={form.taxName}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="taxRate">Tax Rate (%)</label>
            <input
              id="taxRate"
              name="taxRate"
              type="number"
              min="0"
              step="0.01"
              value={form.taxRate}
              onChange={handleChange}
              required
            />
          </div>
        </div>
      </div>
      <button type="submit" className="submit-btn">Generate PDF</button>
    </form>
  );
}
