const STATUS_LABELS = {
  pending: "Chờ thanh toán",
  paid: "Đã thanh toán",
  cancelled: "Đã huỷ",
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
function formatPrice(v) {
  return new Intl.NumberFormat("vi-VN").format(Math.round(v || 0));
}

// ------------------------------------------------------------
// Tabs
// ------------------------------------------------------------
const tabButtons = document.querySelectorAll(".tab-btn");
const panels = {
  invoices: document.getElementById("panel-invoices"),
  customers: document.getElementById("panel-customers"),
  products: document.getElementById("panel-products"),
};

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    Object.entries(panels).forEach(([key, el]) => {
      el.style.display = key === btn.dataset.tab ? "" : "none";
    });
  });
});

// ------------------------------------------------------------
// Hoá đơn (Invoices)
// ------------------------------------------------------------
const invoicesBody = document.getElementById("invoices-body");
const invoicesCount = document.getElementById("invoices-count");
const invoiceModal = document.getElementById("invoice-modal");
const invoiceForm = document.getElementById("invoice-form");
const invoiceFormError = document.getElementById("invoice-form-error");

let customersCache = [];

function customerName(id) {
  const c = customersCache.find((x) => x.id === id);
  return c ? c.customer_name : `#${id}`;
}

function openInvoiceForm(invoice) {
  invoiceFormError.style.display = "none";
  document.getElementById("invoice-form-title").textContent = invoice ? `Sửa hoá đơn #${invoice.id}` : "Tạo hoá đơn";
  document.getElementById("inv-id").value = invoice ? invoice.id : "";
  document.getElementById("inv-customer").value = invoice ? invoice.customer_id : "";
  document.getElementById("inv-total").value = invoice ? invoice.total_amount : "";
  document.getElementById("inv-status").value = invoice ? invoice.status : "pending";
  invoiceModal.style.display = "flex";
}

document.getElementById("add-invoice-btn").addEventListener("click", () => openInvoiceForm(null));
document.getElementById("invoice-form-cancel").addEventListener("click", () => (invoiceModal.style.display = "none"));

invoiceForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  invoiceFormError.style.display = "none";
  const id = document.getElementById("inv-id").value;
  const payload = {
    customer_id: Number(document.getElementById("inv-customer").value),
    total_amount: document.getElementById("inv-total").value ? Number(document.getElementById("inv-total").value) : 0,
    status: document.getElementById("inv-status").value,
  };
  const submitBtn = invoiceForm.querySelector("button[type=submit]");
  submitBtn.disabled = true;
  try {
    if (id) await BillingApi.updateInvoice(id, payload);
    else await BillingApi.createInvoice(payload);
    invoiceModal.style.display = "none";
    loadInvoices();
  } catch (err) {
    invoiceFormError.textContent = err.message || "Lưu thất bại.";
    invoiceFormError.style.display = "block";
  } finally {
    submitBtn.disabled = false;
  }
});

async function loadInvoices() {
  invoicesBody.innerHTML = `<tr><td colspan="5">Đang tải...</td></tr>`;
  try {
    const data = await BillingApi.listInvoices();
    const items = data.items || data || [];
    invoicesCount.textContent = `${data.total ?? items.length} hoá đơn`;
    if (!items.length) {
      invoicesBody.innerHTML = `<tr><td colspan="5">Chưa có hoá đơn nào.</td></tr>`;
      return;
    }
    invoicesBody.innerHTML = items
      .map(
        (inv) => `
      <tr>
        <td>#${inv.id}</td>
        <td>${escapeHtml(customerName(inv.customer_id))}</td>
        <td>${formatPrice(inv.total_amount)}đ</td>
        <td><span class="badge ${inv.status === "paid" ? "confirmed" : inv.status === "cancelled" ? "cancelled" : "pending"}">${
          STATUS_LABELS[inv.status] || inv.status
        }</span></td>
        <td class="actions">
          <button class="btn btn-ghost btn-sm edit-invoice-btn" data-id="${inv.id}">Sửa</button>
          <button class="btn btn-ghost btn-sm del-invoice-btn" data-id="${inv.id}">Xoá</button>
        </td>
      </tr>`
      )
      .join("");
    window.__invoices = items;
    document.querySelectorAll(".edit-invoice-btn").forEach((btn) =>
      btn.addEventListener("click", () => {
        const inv = window.__invoices.find((x) => String(x.id) === btn.dataset.id);
        openInvoiceForm(inv);
      })
    );
    document.querySelectorAll(".del-invoice-btn").forEach((btn) =>
      btn.addEventListener("click", async () => {
        if (!confirm("Xoá hoá đơn này?")) return;
        try {
          await BillingApi.removeInvoice(btn.dataset.id);
          loadInvoices();
        } catch (err) {
          alert(`Không xoá được: ${err.message}`);
        }
      })
    );
  } catch (err) {
    invoicesBody.innerHTML = `<tr><td colspan="5">Không tải được dữ liệu: ${escapeHtml(err.message)}</td></tr>`;
  }
}

// ------------------------------------------------------------
// Khách hàng (Customers)
// ------------------------------------------------------------
const customersBody = document.getElementById("customers-body");
const customersCount = document.getElementById("customers-count");
const customerModal = document.getElementById("customer-modal");
const customerForm = document.getElementById("customer-form");
const customerFormError = document.getElementById("customer-form-error");

function openCustomerForm(customer) {
  customerFormError.style.display = "none";
  document.getElementById("customer-form-title").textContent = customer ? `Sửa: ${customer.customer_name}` : "Thêm khách hàng";
  document.getElementById("cus-id").value = customer ? customer.id : "";
  document.getElementById("cus-name").value = customer ? customer.customer_name : "";
  document.getElementById("cus-email").value = customer ? customer.email || "" : "";
  document.getElementById("cus-phone").value = customer ? customer.phone || "" : "";
  document.getElementById("cus-address").value = customer ? customer.address || "" : "";
  customerModal.style.display = "flex";
}

document.getElementById("add-customer-btn").addEventListener("click", () => openCustomerForm(null));
document.getElementById("customer-form-cancel").addEventListener("click", () => (customerModal.style.display = "none"));

customerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  customerFormError.style.display = "none";
  const id = document.getElementById("cus-id").value;
  const payload = {
    customer_name: document.getElementById("cus-name").value.trim(),
    email: document.getElementById("cus-email").value.trim() || undefined,
    phone: document.getElementById("cus-phone").value.trim() || undefined,
    address: document.getElementById("cus-address").value.trim() || undefined,
  };
  const submitBtn = customerForm.querySelector("button[type=submit]");
  submitBtn.disabled = true;
  try {
    if (id) await BillingApi.updateCustomer(id, payload);
    else await BillingApi.createCustomer(payload);
    customerModal.style.display = "none";
    await loadCustomers();
    loadInvoices(); // tên khách hàng có thể đã đổi, cập nhật lại bảng hoá đơn
  } catch (err) {
    customerFormError.textContent = err.message || "Lưu thất bại.";
    customerFormError.style.display = "block";
  } finally {
    submitBtn.disabled = false;
  }
});

async function loadCustomers() {
  customersBody.innerHTML = `<tr><td colspan="5">Đang tải...</td></tr>`;
  try {
    const data = await BillingApi.listCustomers();
    const items = data.items || data || [];
    customersCache = items;
    customersCount.textContent = `${data.total ?? items.length} khách hàng`;
    if (!items.length) {
      customersBody.innerHTML = `<tr><td colspan="5">Chưa có khách hàng nào.</td></tr>`;
      return;
    }
    customersBody.innerHTML = items
      .map(
        (c) => `
      <tr>
        <td>#${c.id}</td>
        <td>${escapeHtml(c.customer_name)}</td>
        <td>${escapeHtml(c.email || "—")}</td>
        <td>${escapeHtml(c.phone || "—")}</td>
        <td class="actions">
          <button class="btn btn-ghost btn-sm edit-customer-btn" data-id="${c.id}">Sửa</button>
          <button class="btn btn-ghost btn-sm del-customer-btn" data-id="${c.id}">Xoá</button>
        </td>
      </tr>`
      )
      .join("");
    document.querySelectorAll(".edit-customer-btn").forEach((btn) =>
      btn.addEventListener("click", () => {
        const c = customersCache.find((x) => String(x.id) === btn.dataset.id);
        openCustomerForm(c);
      })
    );
    document.querySelectorAll(".del-customer-btn").forEach((btn) =>
      btn.addEventListener("click", async () => {
        if (!confirm("Xoá khách hàng này?")) return;
        try {
          await BillingApi.removeCustomer(btn.dataset.id);
          loadCustomers();
        } catch (err) {
          alert(`Không xoá được: ${err.message}`);
        }
      })
    );
  } catch (err) {
    customersBody.innerHTML = `<tr><td colspan="5">Không tải được dữ liệu: ${escapeHtml(err.message)}</td></tr>`;
  }
}

// ------------------------------------------------------------
// Sản phẩm / Dịch vụ (Products)
// ------------------------------------------------------------
const productsBody = document.getElementById("products-body");
const productsCount = document.getElementById("products-count");
const productModal = document.getElementById("product-modal");
const productForm = document.getElementById("product-form");
const productFormError = document.getElementById("product-form-error");

function openProductForm(product) {
  productFormError.style.display = "none";
  document.getElementById("product-form-title").textContent = product ? `Sửa: ${product.product_name}` : "Thêm sản phẩm";
  document.getElementById("prod-id").value = product ? product.id : "";
  document.getElementById("prod-name").value = product ? product.product_name : "";
  document.getElementById("prod-code").value = product ? product.product_code || "" : "";
  document.getElementById("prod-description").value = product ? product.description || "" : "";
  productModal.style.display = "flex";
}

document.getElementById("add-product-btn").addEventListener("click", () => openProductForm(null));
document.getElementById("product-form-cancel").addEventListener("click", () => (productModal.style.display = "none"));

productForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  productFormError.style.display = "none";
  const id = document.getElementById("prod-id").value;
  const payload = {
    product_name: document.getElementById("prod-name").value.trim(),
    product_code: document.getElementById("prod-code").value.trim() || undefined,
    description: document.getElementById("prod-description").value.trim() || undefined,
  };
  const submitBtn = productForm.querySelector("button[type=submit]");
  submitBtn.disabled = true;
  try {
    if (id) await BillingApi.updateProduct(id, payload);
    else await BillingApi.createProduct(payload);
    productModal.style.display = "none";
    loadProducts();
  } catch (err) {
    productFormError.textContent = err.message || "Lưu thất bại.";
    productFormError.style.display = "block";
  } finally {
    submitBtn.disabled = false;
  }
});

async function loadProducts() {
  productsBody.innerHTML = `<tr><td colspan="5">Đang tải...</td></tr>`;
  try {
    const data = await BillingApi.listProducts();
    const items = data.items || data || [];
    productsCount.textContent = `${data.total ?? items.length} sản phẩm`;
    if (!items.length) {
      productsBody.innerHTML = `<tr><td colspan="5">Chưa có sản phẩm nào.</td></tr>`;
      return;
    }
    productsBody.innerHTML = items
      .map(
        (p) => `
      <tr>
        <td>#${p.id}</td>
        <td>${escapeHtml(p.product_name)}</td>
        <td>${escapeHtml(p.product_code || "—")}</td>
        <td>${escapeHtml(p.description || "—")}</td>
        <td class="actions">
          <button class="btn btn-ghost btn-sm edit-product-btn" data-id="${p.id}">Sửa</button>
          <button class="btn btn-ghost btn-sm del-product-btn" data-id="${p.id}">Xoá</button>
        </td>
      </tr>`
      )
      .join("");
    window.__products = items;
    document.querySelectorAll(".edit-product-btn").forEach((btn) =>
      btn.addEventListener("click", () => {
        const p = window.__products.find((x) => String(x.id) === btn.dataset.id);
        openProductForm(p);
      })
    );
    document.querySelectorAll(".del-product-btn").forEach((btn) =>
      btn.addEventListener("click", async () => {
        if (!confirm("Xoá sản phẩm này?")) return;
        try {
          await BillingApi.removeProduct(btn.dataset.id);
          loadProducts();
        } catch (err) {
          alert(`Không xoá được: ${err.message}`);
        }
      })
    );
  } catch (err) {
    productsBody.innerHTML = `<tr><td colspan="5">Không tải được dữ liệu: ${escapeHtml(err.message)}</td></tr>`;
  }
}

// ------------------------------------------------------------
// Khởi động: nạp khách hàng trước để bảng hoá đơn map được tên
// ------------------------------------------------------------
if (requireAdmin()) {
  initAdminNav("billing");
  (async () => {
    await loadCustomers();
    loadInvoices();
    loadProducts();
  })();
}
