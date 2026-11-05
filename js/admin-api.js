(function () {
    const BASE = "http://127.0.0.1:8000/api";

    async function request(path, options) {
        const headers = Object.assign(
            { Authorization: "Token " + (localStorage.getItem("smartdineToken") || "") },
            (options && options.headers) || {}
        );
        const settings = Object.assign({}, options || {}, { headers: headers });
        if (settings.body) headers["Content-Type"] = "application/json";

        let response;
        try {
            response = await fetch(BASE + path, settings);
        } catch (error) {
            throw new Error("Cannot connect to Django. Start the backend at 127.0.0.1:8000.");
        }

        let data = {};
        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        if (!response.ok) {
            const detail = data.detail || data.error ||
                Object.entries(data).map(([field, value]) =>
                    field + ": " + (Array.isArray(value) ? value.join(", ") : value)
                ).join(" | ");
            if (response.status === 401) {
                localStorage.removeItem("smartdineToken");
                localStorage.removeItem("smartdineUser");
            }
            throw new Error(detail || "Request failed (" + response.status + ").");
        }
        return data;
    }

    async function requireAdmin() {
        if (!localStorage.getItem("smartdineToken")) {
            const page = window.location.pathname.split("/").pop();
            window.location.href = "../login.html?next=admin%20pannel/" +
                encodeURIComponent(page);
            return false;
        }
        try {
            await request("/users/admin/overview/");
            return true;
        } catch (error) {
            const content = document.querySelector(".main-content");
            if (content) {
                content.innerHTML = "";
                const message = document.createElement("section");
                message.className = "admin-access-error";
                message.textContent = error.message.includes("Administrator")
                    ? "This page is available only to administrators."
                    : error.message;
                content.appendChild(message);
            }
            return false;
        }
    }

    async function requireRestaurantManager() {
        if (!localStorage.getItem("smartdineToken")) {
            const page = window.location.pathname.split("/").pop();
            window.location.href = "../login.html?next=admin%20pannel/" +
                encodeURIComponent(page) + window.location.search;
            return null;
        }
        try {
            const user = await request("/users/profile/");
            if (user.user_type === "restaurant_owner" || user.is_staff) return user;
            throw new Error("Restaurant-owner or administrator access required.");
        } catch (error) {
            const content = document.querySelector(".main-content") ||
                document.querySelector(".menu-admin");
            if (content) {
                content.innerHTML = "";
                const message = document.createElement("section");
                message.className = "admin-access-error";
                message.textContent = error.message;
                content.appendChild(message);
            }
            return null;
        }
    }

    window.SmartDineAdminAPI = {
        request: request,
        requireAdmin: requireAdmin,
        requireRestaurantManager: requireRestaurantManager
    };
})();
