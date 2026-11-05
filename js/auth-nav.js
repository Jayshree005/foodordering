(function () {
    const tokenKey = "smartdineToken";
    const userKey = "smartdineUser";
    const apiBase = "http://127.0.0.1:8000/api";

    function readUser() {
        try {
            return JSON.parse(localStorage.getItem(userKey) || "null");
        } catch (error) {
            console.error("Unable to read the saved user profile:", error);
            return null;
        }
    }

    function displayName(user) {
        if (!user) return "My Profile";
        const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ").trim();
        return fullName || user.username || user.email || "My Profile";
    }

    function createLink(href, text, className, isLogout) {
        const link = document.createElement("a");
        link.href = href;
        link.textContent = text;
        link.className = className;
        link.dataset.authGenerated = "true";
        if (isLogout) link.dataset.logout = "true";
        return link;
    }

    function renderSignedIn(user) {
        const label = "Hi, " + displayName(user);
        const isRestaurantOwner = user && user.user_type === "restaurant_owner";
        const actions = document.querySelector(".nav-actions");
        if (actions) {
            actions.querySelectorAll(".login-btn, .signup-btn").forEach(link => {
                link.hidden = true;
            });
            let accountLink = actions.querySelector("[data-auth-account]");
            if (!accountLink) {
                accountLink = createLink("profile.html", label, "account-nav-link");
                accountLink.dataset.authAccount = "true";
                actions.appendChild(accountLink);
            }
            accountLink.textContent = label;
            if (!actions.querySelector("[data-auth-logout]")) {
                const logoutLink = createLink("#", "Log out", "logout-nav-link", true);
                logoutLink.dataset.authLogout = "true";
                actions.appendChild(logoutLink);
            }
            if (isRestaurantOwner && !actions.querySelector("[data-auth-manager]")) {
                const managerLink = createLink(
                    "admin%20pannel/restaurants-management.html",
                    "Manage Restaurants",
                    "account-nav-link"
                );
                managerLink.dataset.authManager = "true";
                actions.appendChild(managerLink);
            }
        }

        const mobileMenu = document.querySelector(".mobile-menu");
        if (mobileMenu) {
            const loginLink = mobileMenu.querySelector('a[href="login.html"]');
            const signupLink = mobileMenu.querySelector('a[href="signup.html"]');
            if (loginLink) loginLink.hidden = true;
            if (signupLink) signupLink.hidden = true;

            let accountLink = mobileMenu.querySelector("[data-auth-account]");
            if (!accountLink) {
                accountLink = createLink("profile.html", label, "account-nav-link");
                accountLink.dataset.authAccount = "true";
                mobileMenu.appendChild(accountLink);
            }
            accountLink.textContent = label;
            if (!mobileMenu.querySelector("[data-auth-logout]")) {
                const logoutLink = createLink("#", "Log out", "logout-nav-link", true);
                logoutLink.dataset.authLogout = "true";
                mobileMenu.appendChild(logoutLink);
            }
            if (isRestaurantOwner && !mobileMenu.querySelector("[data-auth-manager]")) {
                const managerLink = createLink(
                    "admin%20pannel/restaurants-management.html",
                    "Manage Restaurants",
                    "account-nav-link"
                );
                managerLink.dataset.authManager = "true";
                mobileMenu.appendChild(managerLink);
            }
        }

        const navLinks = document.querySelector(".nav-links");
        if (!actions && navLinks) {
            let accountLink = navLinks.querySelector("[data-auth-account]");
            if (!accountLink) {
                accountLink = createLink("profile.html", label, "account-nav-link");
                accountLink.dataset.authAccount = "true";
                navLinks.appendChild(accountLink);
            }
            accountLink.textContent = label;
            if (!navLinks.querySelector("[data-auth-logout]")) {
                const logoutLink = createLink("#", "Log out", "logout-nav-link", true);
                logoutLink.dataset.authLogout = "true";
                navLinks.appendChild(logoutLink);
            }
            if (isRestaurantOwner && !navLinks.querySelector("[data-auth-manager]")) {
                const managerLink = createLink(
                    "admin%20pannel/restaurants-management.html",
                    "Manage Restaurants",
                    "account-nav-link"
                );
                managerLink.dataset.authManager = "true";
                navLinks.appendChild(managerLink);
            }
        }

        if (!mobileMenu) {
            const navbar = document.querySelector(".navbar");
            if (navbar) {
                let mobileControls = navbar.querySelector("[data-auth-mobile]");
                if (!mobileControls) {
                    mobileControls = document.createElement("div");
                    mobileControls.className = "mobile-account-controls";
                    mobileControls.dataset.authGenerated = "true";
                    mobileControls.dataset.authMobile = "true";
                    const accountLink = createLink("profile.html", label, "account-nav-link");
                    accountLink.dataset.authAccount = "true";
                    mobileControls.appendChild(accountLink);
                    const logoutLink = createLink("#", "Log out", "logout-nav-link", true);
                    logoutLink.dataset.authLogout = "true";
                    mobileControls.appendChild(logoutLink);
                    if (isRestaurantOwner) {
                        const managerLink = createLink(
                            "admin%20pannel/restaurants-management.html",
                            "Manage Restaurants",
                            "account-nav-link"
                        );
                        managerLink.dataset.authManager = "true";
                        mobileControls.appendChild(managerLink);
                    }
                    const actions = navbar.querySelector(".nav-actions");
                    if (actions) actions.after(mobileControls);
                    else navbar.appendChild(mobileControls);
                }
                mobileControls.querySelector("[data-auth-account]").textContent = label;
            }
        }
    }

    function renderSignedOut() {
        document.querySelectorAll("[data-auth-generated]").forEach(link => link.remove());
        document.querySelectorAll(".nav-actions .login-btn, .nav-actions .signup-btn, " +
            ".mobile-menu a[href='login.html'], .mobile-menu a[href='signup.html']")
            .forEach(link => { link.hidden = false; });
    }

    function logout() {
        localStorage.removeItem(tokenKey);
        localStorage.removeItem(userKey);
        renderSignedOut();
        window.location.href = "index.html";
    }

    document.addEventListener("click", event => {
        const logoutLink = event.target.closest("[data-logout]");
        if (logoutLink) {
            event.preventDefault();
            logout();
        }
    });

    window.addEventListener("storage", event => {
        if (event.key === tokenKey || event.key === userKey) {
            if (localStorage.getItem(tokenKey)) renderSignedIn(readUser());
            else renderSignedOut();
        }
    });

    const token = localStorage.getItem(tokenKey);
    if (!token) {
        renderSignedOut();
        return;
    }

    renderSignedIn(readUser());
    fetch(apiBase + "/users/profile/", {
        headers: { Authorization: "Token " + token }
    }).then(async response => {
        if (response.status === 401) {
            localStorage.removeItem(tokenKey);
            localStorage.removeItem(userKey);
            renderSignedOut();
            return;
        }
        if (!response.ok) {
            throw new Error("Unable to verify the signed-in user (" + response.status + ").");
        }
        const user = await response.json();
        localStorage.setItem(userKey, JSON.stringify(user));
        renderSignedIn(user);
    }).catch(error => {
        console.error("Unable to refresh the signed-in user:", error);
    });
})();
