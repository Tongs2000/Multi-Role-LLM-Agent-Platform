document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const productsContainer = document.getElementById('products');
    const cartContainer = document.getElementById('cart');
    const totalElement = document.getElementById('total');
    const clearCartBtn = document.getElementById('clear-cart');

    // Load products and cart on page load
    loadProducts();
    loadCart();

    // Event listeners
    clearCartBtn.addEventListener('click', clearCart);

    // Functions
    async function loadProducts() {
        try {
            const response = await fetch('/api/products');
            const products = await response.json();
            
            productsContainer.innerHTML = '';
            products.forEach(product => {
                const productElement = document.createElement('div');
                productElement.className = 'product';
                productElement.innerHTML = `
                    <h3>${product.name}</h3>
                    <p>$${product.price.toFixed(2)}</p>
                    <p>Stock: ${product.stock}</p>
                    <button onclick="addToCart(${product.id})">Add to Cart</button>
                `;
                productsContainer.appendChild(productElement);
            });
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }

    async function loadCart() {
        try {
            const response = await fetch('/api/cart');
            const cartData = await response.json();
            
            cartContainer.innerHTML = '';
            if (cartData.items.length === 0) {
                cartContainer.innerHTML = '<p>Your cart is empty</p>';
                totalElement.textContent = '0.00';
                return;
            }
            
            cartData.items.forEach(item => {
                const cartItemElement = document.createElement('div');
                cartItemElement.className = 'cart-item';
                cartItemElement.innerHTML = `
                    <div>
                        <strong>${item.product.name}</strong>
                        <p>$${item.product.price.toFixed(2)} each</p>
                    </div>
                    <div class="cart-item-controls">
                        <button onclick="updateCartItem(${item.product_id}, ${item.quantity - 1})">-</button>
                        <span>${item.quantity}</span>
                        <button onclick="updateCartItem(${item.product_id}, ${item.quantity + 1})">+</button>
                    </div>
                `;
                cartContainer.appendChild(cartItemElement);
            });
            
            totalElement.textContent = cartData.total.toFixed(2);
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    }

    async function clearCart() {
        try {
            await fetch('/api/cart/clear', {
                method: 'POST'
            });
            loadCart();
        } catch (error) {
            console.error('Error clearing cart:', error);
        }
    }

    // Make functions available globally
    window.addToCart = async function(productId) {
        try {
            await fetch('/api/cart/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            });
            loadCart();
        } catch (error) {
            console.error('Error adding to cart:', error);
        }
    };

    window.updateCartItem = async function(productId, quantity) {
        try {
            await fetch('/api/cart/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    product_id: productId,
                    quantity: quantity 
                })
            });
            loadCart();
        } catch (error) {
            console.error('Error updating cart:', error);
        }
    };
});