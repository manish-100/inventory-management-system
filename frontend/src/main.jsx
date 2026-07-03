import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import axios from 'axios';
import './style.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const api = axios.create({ baseURL: API_BASE });

const emptyProduct = { name: '', sku: '', description: '', price: '', stock: '' };
const emptyCustomer = { name: '', email: '', phone: '', address: '' };
const emptyOrder = { customer_id: '', product_id: '', quantity: 1 };
const defaultDashboard = { totalProducts: 0, totalCustomers: 0, totalOrders: 0, lowStockProducts: 0 };

function App() {
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [dashboard, setDashboard] = useState(defaultDashboard);
  const [product, setProduct] = useState(emptyProduct);
  const [customer, setCustomer] = useState(emptyCustomer);
  const [order, setOrder] = useState(emptyOrder);
  const [productSearch, setProductSearch] = useState('');
  const [customerSearch, setCustomerSearch] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const errorText = (error) => error.response?.data?.detail || error.message || 'Something went wrong';

  async function loadData() {
    const [productRes, customerRes, orderRes, dashboardRes] = await Promise.all([
      api.get('/products/', { params: productSearch ? { search: productSearch } : {} }),
      api.get('/customers/', { params: customerSearch ? { search: customerSearch } : {} }),
      api.get('/orders/'),
      api.get('/dashboard/'),
    ]);
    setProducts(productRes.data);
    setCustomers(customerRes.data);
    setOrders(orderRes.data);
    setDashboard(dashboardRes.data);
  }

  useEffect(() => {
    loadData().catch((error) => setMessage(errorText(error)));
  }, [productSearch, customerSearch]);

  async function handleAction(action, successMessage) {
    setLoading(true);
    setMessage('');
    try {
      await action();
      await loadData();
      setMessage(successMessage);
    } catch (error) {
      setMessage(errorText(error));
    } finally {
      setLoading(false);
    }
  }

  function addProduct(event) {
    event.preventDefault();
    handleAction(async () => {
      await api.post('/products/', {
        ...product,
        price: Number(product.price),
        stock: Number(product.stock),
      });
      setProduct(emptyProduct);
    }, 'Product saved successfully');
  }

  function addCustomer(event) {
    event.preventDefault();
    handleAction(async () => {
      await api.post('/customers/', customer);
      setCustomer(emptyCustomer);
    }, 'Customer saved successfully');
  }

  function placeOrder(event) {
    event.preventDefault();
    handleAction(async () => {
      await api.post('/orders/', {
        customer_id: Number(order.customer_id),
        items: [{ product_id: Number(order.product_id), quantity: Number(order.quantity) }],
      });
      setOrder(emptyOrder);
    }, 'Order placed successfully. Stock was reduced automatically.');
  }

  function deleteItem(type, id) {
    if (!window.confirm('Are you sure you want to delete this record?')) return;
    handleAction(async () => {
      await api.delete(`/${type}/${id}`);
    }, 'Deleted successfully');
  }

  function cancelOrder(id) {
    if (!window.confirm('Cancel this order? Stock will be added back.')) return;
    handleAction(async () => {
      await api.patch(`/orders/${id}/cancel`);
    }, 'Order cancelled successfully. Stock was restored.');
  }

  function changeOrderStatus(id, status) {
    handleAction(async () => {
      await api.patch(`/orders/${id}/status`, { status });
    }, `Order status changed to ${status}`);
  }

  const availableProducts = useMemo(() => products.filter((p) => Number(p.stock) > 0), [products]);

  return (
    <div className="container">
      <header className="hero">
        <div>
          <h1>Inventary Order System</h1>
          <p>Manage products, customers, orders and automatic inventary tracking.</p>
        </div>
        <span className="badge">FastAPI + React + PostgreSQL</span>
      </header>

      <section className="dashboard-grid">
        <SummaryCard title="Total Products" value={dashboard.totalProducts} />
        <SummaryCard title="Total Customers" value={dashboard.totalCustomers} />
        <SummaryCard title="Total Orders" value={dashboard.totalOrders} />
        <SummaryCard title="Low Stock Products" value={dashboard.lowStockProducts} warning />
      </section>

      {message && <div className="alert">{message}</div>}
      {loading && <div className="alert info">Processing...</div>}

      <div className="grid">
        <section className="card">
          <h2>Add Product</h2>
          <form onSubmit={addProduct}>
            <input placeholder="Product name" value={product.name} onChange={(e) => setProduct({ ...product, name: e.target.value })} required />
            <input placeholder="Unique SKU" value={product.sku} onChange={(e) => setProduct({ ...product, sku: e.target.value })} required />
            <input placeholder="Description" value={product.description} onChange={(e) => setProduct({ ...product, description: e.target.value })} />
            <input placeholder="Price" type="number" min="1" step="0.01" value={product.price} onChange={(e) => setProduct({ ...product, price: e.target.value })} required />
            <input placeholder="Stock quantity" type="number" min="0" value={product.stock} onChange={(e) => setProduct({ ...product, stock: e.target.value })} required />
            <button disabled={loading}>Save Product</button>
          </form>
        </section>

        <section className="card">
          <h2>Add Customer</h2>
          <form onSubmit={addCustomer}>
            <input placeholder="Customer name" value={customer.name} onChange={(e) => setCustomer({ ...customer, name: e.target.value })} required />
            <input placeholder="Unique email" type="email" value={customer.email} onChange={(e) => setCustomer({ ...customer, email: e.target.value })} required />
            <input placeholder="Phone" value={customer.phone} onChange={(e) => setCustomer({ ...customer, phone: e.target.value })} />
            <input placeholder="Address" value={customer.address} onChange={(e) => setCustomer({ ...customer, address: e.target.value })} />
            <button disabled={loading}>Save Customer</button>
          </form>
        </section>

        <section className="card">
          <h2>Place Order</h2>
          <form onSubmit={placeOrder}>
            <select value={order.customer_id} onChange={(e) => setOrder({ ...order, customer_id: e.target.value })} required>
              <option value="">Select customer</option>
              {customers.map((c) => <option key={c.id} value={c.id}>{c.name} - {c.email}</option>)}
            </select>
            <select value={order.product_id} onChange={(e) => setOrder({ ...order, product_id: e.target.value })} required>
              <option value="">Select product</option>
              {availableProducts.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.sku}) - Stock: {p.stock}</option>)}
            </select>
            <input type="number" min="1" value={order.quantity} onChange={(e) => setOrder({ ...order, quantity: e.target.value })} required />
            <button disabled={loading}>Place Order</button>
          </form>
        </section>
      </div>

      <DataTable
        title="Products"
        headers={["Name", "SKU", "Price", "Stock", "Action"]}
        searchValue={productSearch}
        onSearchChange={setProductSearch}
        searchPlaceholder="Search by product name or SKU"
      >
        {products.map((p) => (
          <tr key={p.id} className={Number(p.stock) < 5 ? 'low-stock-row' : ''}>
            <td>{p.name}</td><td>{p.sku}</td><td>₹{p.price}</td>
            <td>{p.stock} {Number(p.stock) < 5 && <span className="low-stock">Low stock</span>}</td>
            <td><button className="danger" onClick={() => deleteItem('products', p.id)}>Delete</button></td>
          </tr>
        ))}
      </DataTable>

      <DataTable
        title="Customers"
        headers={["Name", "Email", "Phone", "Action"]}
        searchValue={customerSearch}
        onSearchChange={setCustomerSearch}
        searchPlaceholder="Search by customer name or email"
      >
        {customers.map((c) => (
          <tr key={c.id}>
            <td>{c.name}</td><td>{c.email}</td><td>{c.phone || '-'}</td>
            <td><button className="danger" onClick={() => deleteItem('customers', c.id)}>Delete</button></td>
          </tr>
        ))}
      </DataTable>

      <DataTable title="Orders" headers={["Order", "Customer", "Items", "Total", "Status", "Action"]}>
        {orders.map((o) => (
          <tr key={o.id}>
            <td>#{o.id}</td>
            <td>{o.customer?.name}</td>
            <td>{o.items.map((i) => `${i.product.name} x ${i.quantity}`).join(', ')}</td>
            <td>₹{o.total_amount}</td>
            <td>
              <span className={`status ${o.status.toLowerCase()}`}>{o.status}</span>
              {o.status !== 'CANCELLED' && (
                <select className="status-select" value={o.status} onChange={(e) => changeOrderStatus(o.id, e.target.value)}>
                  <option value="PLACED">PLACED</option>
                  <option value="COMPLETED">COMPLETED</option>
                  <option value="CANCELLED">CANCELLED</option>
                </select>
              )}
            </td>
            <td className="action-cell">
              {o.status !== 'CANCELLED' && <button className="warning" onClick={() => cancelOrder(o.id)}>Cancel</button>}
              <button className="danger" onClick={() => deleteItem('orders', o.id)}>Delete</button>
            </td>
          </tr>
        ))}
      </DataTable>
    </div>
  );
}

function SummaryCard({ title, value, warning }) {
  return (
    <section className={`summary-card ${warning && Number(value) > 0 ? 'warning-card' : ''}`}>
      <p>{title}</p>
      <h3>{value}</h3>
    </section>
  );
}

function DataTable({ title, headers, children, searchValue, onSearchChange, searchPlaceholder }) {
  return (
    <section className="card">
      <div className="section-head">
        <h2>{title}</h2>
        {onSearchChange && (
          <input className="search-input" placeholder={searchPlaceholder} value={searchValue} onChange={(e) => onSearchChange(e.target.value)} />
        )}
      </div>
      <div className="table-wrapper">
        <table>
          <thead><tr>{headers.map((h) => <th key={h}>{h}</th>)}</tr></thead>
          <tbody>{children}</tbody>
        </table>
      </div>
    </section>
  );
}

createRoot(document.getElementById('root')).render(<App />);
