// Shared client for the local Django REST API.
(function () {
    const API_BASE = "http://127.0.0.1:8000/api";
    const CART_KEY = "smartdineCart";
    const TOKEN_KEY = "smartdineToken";

    async function request(path, options) {
        const requestOptions = Object.assign({}, options || {});
        const headers = Object.assign({}, requestOptions.headers || {});
        const token = localStorage.getItem(TOKEN_KEY);

        if (token) {
            headers.Authorization = "Token " + token;
        }

        if (requestOptions.body && !headers["Content-Type"]) {
            headers["Content-Type"] = "application/json";
        }

        requestOptions.headers = headers;

        let response;
        try {
            response = await fetch(API_BASE + path, requestOptions);
        } catch (error) {
            throw new Error("Cannot connect to the backend. Check that Django is running at 127.0.0.1:8000.");
        }

        let data;
        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem(TOKEN_KEY);
                localStorage.removeItem("smartdineUser");
            }

            const details = data.error || data.detail ||
                Object.entries(data).map(([field, value]) =>
                    field + ": " + (Array.isArray(value) ? value.join(", ") : value)
                ).join(" | ");
            throw new Error(details || "The backend request failed (" + response.status + ").");
        }

        return data;
    }

    function readLocalCart() {
        try {
            const cart = JSON.parse(localStorage.getItem(CART_KEY) || "[]");
            return Array.isArray(cart) ? cart : [];
        } catch (error) {
            console.error("Unable to read the saved cart:", error);
            return [];
        }
    }

    function saveLocalCart(cart) {
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
    }

    function flattenCarts(data) {
        const result = [];
        (data.carts || []).forEach(cart => {
            (cart.items || []).forEach(item => {
                result.push({
                    id: item.food_item,
                    server_item_id: item.id,
                    name: item.food_name,
                    price: Number(item.price),
                    image: item.image || "",
                    restaurant_id: cart.restaurant,
                    quantity: Number(item.quantity),
                    customizations: item.customizations || []
                });
            });
        });
        return result;
    }

    async function loadCart() {
        if (!localStorage.getItem(TOKEN_KEY)) {
            return readLocalCart();
        }
        const data = await request("/cart/");
        const cart = flattenCarts(data);
        saveLocalCart(cart);
        return cart;
    }

    async function syncGuestCart() {
        const token = localStorage.getItem(TOKEN_KEY);
        if (!token) {
            return readLocalCart();
        }

        const guestCart = readLocalCart();
        let remoteCart = flattenCarts(await request("/cart/"));
        const cartKey = item => [
            String(item.id),
            JSON.stringify([...(item.customizations || [])].sort())
        ].join(":");
        const existingByFood = new Map(remoteCart.map(item => [cartKey(item), item]));

        for (const item of guestCart) {
            const existing = existingByFood.get(cartKey(item));
            const missingQuantity = Math.max(
                0,
                Number(item.quantity || 1) - Number(existing ? existing.quantity : 0)
            );
            if (missingQuantity > 0) {
                await request("/cart/add/", {
                    method: "POST",
                    body: JSON.stringify({
                        food_item_id: item.id,
                        quantity: missingQuantity,
                        customizations: item.customizations || []
                    })
                });
            }
        }

        remoteCart = flattenCarts(await request("/cart/"));
        saveLocalCart(remoteCart);
        return remoteCart;
    }

    async function addCartItem(food, restaurantId, customizations) {
        if (localStorage.getItem(TOKEN_KEY)) {
            await request("/cart/add/", {
                method: "POST",
                body: JSON.stringify({
                    food_item_id: food.id,
                    quantity: 1,
                    customizations: customizations || []
                })
            });
            return loadCart();
        }

        const cart = readLocalCart();
        const otherRestaurant = cart.find(
            item => String(item.restaurant_id) !== String(restaurantId)
        );
        if (otherRestaurant) {
            throw new Error("Please finish or clear your current restaurant cart before adding food from another restaurant.");
        }

        const selectedCustomizations = customizations || [];
        const customizationKey = values => JSON.stringify([...values].sort());
        const item = cart.find(entry =>
            String(entry.id) === String(food.id) &&
            customizationKey(entry.customizations || []) === customizationKey(selectedCustomizations)
        );
        if (item) {
            item.quantity += 1;
        } else {
            cart.push({
                id: food.id,
                name: food.name,
                price: Number(food.price),
                image: food.image || "",
                restaurant_id: restaurantId,
                quantity: 1,
                customizations: selectedCustomizations
            });
        }
        saveLocalCart(cart);
        return cart;
    }

    async function updateCartItem(item, quantity) {
        if (localStorage.getItem(TOKEN_KEY)) {
            if (!quantity) {
                await request("/cart/remove/" + item.server_item_id + "/", {
                    method: "DELETE"
                });
            } else {
                await request("/cart/update/" + item.server_item_id + "/", {
                    method: "PATCH",
                    body: JSON.stringify({ quantity: quantity })
                });
            }
            return loadCart();
        }

        const cart = readLocalCart();
        const index = cart.findIndex(entry => String(entry.id) === String(item.id));
        if (index >= 0) {
            if (quantity < 1) {
                cart.splice(index, 1);
            } else {
                cart[index].quantity = quantity;
            }
        }
        saveLocalCart(cart);
        return cart;
    }

    async function clearCart() {
        if (localStorage.getItem(TOKEN_KEY)) {
            const cart = await loadCart();
            const restaurantIds = Array.from(new Set(cart.map(item => item.restaurant_id)));
            for (const restaurantId of restaurantIds) {
                await request("/cart/clear/?restaurant_id=" + encodeURIComponent(restaurantId), {
                    method: "DELETE"
                });
            }
        }
        saveLocalCart([]);
        return [];
    }

    window.SmartDineAPI = {
        request: request,
        readLocalCart: readLocalCart,
        saveLocalCart: saveLocalCart,
        loadCart: loadCart,
        syncGuestCart: syncGuestCart,
        addCartItem: addCartItem,
        updateCartItem: updateCartItem,
        clearCart: clearCart
    };
})();
