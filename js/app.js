
// SMARTDINE - MOBILE MENU + MULTILINGUAL SUPPORT

const menuToggle = document.getElementById("menuToggle");
const mobileMenu = document.getElementById("mobileMenu");

const languageSelect = document.getElementById("languageSelect");
const mobileLanguageSelect = document.getElementById("mobileLanguageSelect");

// MOBILE NAVIGATION
if (menuToggle && mobileMenu) {

    menuToggle.addEventListener("click", () => {
        mobileMenu.classList.toggle("show");
        menuToggle.classList.toggle("active");

        const isOpen = mobileMenu.classList.contains("show");

        menuToggle.setAttribute("aria-expanded", isOpen);
        menuToggle.setAttribute(
            "aria-label",
            isOpen ? "Close menu" : "Open menu"
        );
    });

    mobileMenu.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            mobileMenu.classList.remove("show");
            menuToggle.classList.remove("active");
            menuToggle.setAttribute("aria-expanded", "false");
        });
    });

    document.addEventListener("click", event => {
        if (
            !mobileMenu.contains(event.target) &&
            !menuToggle.contains(event.target)
        ) {
            mobileMenu.classList.remove("show");
            menuToggle.classList.remove("active");
            menuToggle.setAttribute("aria-expanded", "false");
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 768) {
            mobileMenu.classList.remove("show");
            menuToggle.classList.remove("active");
            menuToggle.setAttribute("aria-expanded", "false");
        }
    });
}

// WEBSITE TRANSLATIONS
const translations = {

    en: {
        nav: ["Home", "Restaurants", "About", "Contact", "Offers"],
        heroTag: "✦ GLOBAL CUISINE, LOCAL LOVE",
        heroTitle: "Discover Amazing Food|From Multiple Restaurants",
        heroText: "Explore top restaurants, enjoy special menus for international guests and order your favourite food with SmartDine.",
        heroButtons: ["Explore Restaurants →", "Learn More"],
        stats: ["Multiple", "Restaurants", "6 Languages", "Multi-Lingual Support", "Smart", "Food Experience"],
        quick: [
            "Special Menu for Foreign Guests",
            "Discover international cuisines",
            "Multi-Lingual Support",
            "Switch between languages",
            "Live Order Tracking",
            "Know your order status",
            "Smart Recommendations",
            "Find dishes you'll love"
        ],
        internationalHeading: "Explore International Cuisine",
        internationalTag: "FOOD WITHOUT BORDERS",
        internationalText: "Special food choices and menus for guests from around the world.",
        cuisines: [
            "Italian Cuisine", "Pizza, pasta and delicious Italian favourites.",
            "Japanese Cuisine", "Explore sushi, noodles and Japanese dishes.",
            "Indian Cuisine", "Discover traditional Indian flavours and meals.",
            "Continental Cuisine", "Enjoy popular continental food selections."
        ],
        restaurantTag: "EXPLORE OUR RESTAURANTS",
        restaurantHeading: "Popular Restaurants",
        restaurantText: "Find your favourite restaurant and discover something delicious.",
        restaurants: [
            "Italian Bistro", "Italian · Continental",
            "The Spice House", "Indian · North Indian",
            "Sushi Place", "Japanese · Sushi",
            "Burger Hub", "Fast Food · Burgers"
        ],
        viewAll: "View All Restaurants →",
        footerTagline: "Good Food. Good Mood.",
        footerDescription: "Discover restaurants, explore cuisines and enjoy a smarter food ordering experience.",
        footerHeadings: ["Quick Links", "Support", "Contact Us", "Follow Us"],
        footerLinks: [
            "Home", "Restaurants", "About Us", "Special Menus", "Contact",
            "FAQ", "Help Center", "Terms & Conditions", "Privacy Policy"
        ],
        location: "📍 New Delhi, India",
        copyright: "© 2026 SmartDine. All Rights Reserved.",
        footerLove: "Made with ❤️ for Food Lovers"
    },

    hi: {
        nav: ["होम", "रेस्टोरेंट", "हमारे बारे में", "संपर्क", "ऑफर्स"],
        heroTag: "✦ दुनिया भर का स्वाद, आपके शहर में",
        heroTitle: "स्वादिष्ट खाने की खोज करें|कई रेस्टोरेंट से",
        heroText: "बेहतरीन रेस्टोरेंट खोजें, विदेशी मेहमानों के लिए विशेष मेनू देखें और SmartDine के साथ अपना पसंदीदा खाना ऑर्डर करें।",
        heroButtons: ["रेस्टोरेंट देखें →", "और जानें"],
        stats: ["कई", "रेस्टोरेंट", "6 भाषाएँ", "बहुभाषी सुविधा", "स्मार्ट", "खाने का अनुभव"],
        quick: [
            "विदेशी मेहमानों के लिए विशेष मेनू",
            "अंतरराष्ट्रीय व्यंजन खोजें",
            "बहुभाषी सुविधा",
            "अपनी भाषा चुनें",
            "ऑर्डर ट्रैकिंग",
            "अपने ऑर्डर का स्टेटस जानें",
            "स्मार्ट सुझाव",
            "अपनी पसंद के व्यंजन खोजें"
        ],
        internationalHeading: "अंतरराष्ट्रीय व्यंजन खोजें",
        internationalTag: "स्वाद की कोई सीमा नहीं",
        internationalText: "दुनिया भर के मेहमानों के लिए खास भोजन और मेनू।",
        cuisines: [
            "इटैलियन व्यंजन", "पिज्जा, पास्ता और स्वादिष्ट इटैलियन खाना।",
            "जापानी व्यंजन", "सुशी, नूडल्स और जापानी खाना।",
            "भारतीय व्यंजन", "पारंपरिक भारतीय स्वाद और भोजन।",
            "कॉन्टिनेंटल व्यंजन", "लोकप्रिय कॉन्टिनेंटल भोजन का आनंद लें।"
        ],
        restaurantTag: "हमारे रेस्टोरेंट देखें",
        restaurantHeading: "लोकप्रिय रेस्टोरेंट",
        restaurantText: "अपना पसंदीदा रेस्टोरेंट चुनें और स्वादिष्ट खाने का आनंद लें।",
        restaurants: [
            "इटैलियन बिस्ट्रो", "इटैलियन · कॉन्टिनेंटल",
            "द स्पाइस हाउस", "भारतीय · उत्तर भारतीय",
            "सुशी प्लेस", "जापानी · सुशी",
            "बर्गर हब", "फास्ट फूड · बर्गर"
        ],
        viewAll: "सभी रेस्टोरेंट देखें →",
        footerTagline: "अच्छा खाना। अच्छा मूड।",
        footerDescription: "रेस्टोरेंट खोजें, अलग-अलग व्यंजनों का आनंद लें और स्मार्ट तरीके से खाना ऑर्डर करें।",
        footerHeadings: ["क्विक लिंक", "सहायता", "संपर्क करें", "हमें फॉलो करें"],
        footerLinks: [
            "होम", "रेस्टोरेंट", "हमारे बारे में", "विशेष मेनू", "संपर्क",
            "सामान्य प्रश्न", "हेल्प सेंटर", "नियम और शर्तें", "प्राइवेसी पॉलिसी"
        ],
        location: "📍 नई दिल्ली, भारत",
        copyright: "© 2026 SmartDine. सर्वाधिकार सुरक्षित।",
        footerLove: "❤️ खाने के शौकीनों के लिए बनाया गया"
    },

    fr: {
        nav: ["Accueil", "Restaurants", "À propos", "Contact", "Offres"],
        heroTag: "✦ CUISINE DU MONDE, PLAISIR LOCAL",
        heroTitle: "Découvrez des plats délicieux|Dans plusieurs restaurants",
        heroText: "Explorez les meilleurs restaurants, découvrez des menus spéciaux pour les visiteurs internationaux et commandez vos plats préférés avec SmartDine.",
        heroButtons: ["Explorer les restaurants →", "En savoir plus"],
        stats: ["Plusieurs", "Restaurants", "6 langues", "Support multilingue", "Intelligent", "Expérience culinaire"],
        quick: [
            "Menu spécial pour les visiteurs",
            "Découvrez les cuisines du monde",
            "Support multilingue",
            "Changez de langue",
            "Suivi des commandes",
            "Suivez votre commande",
            "Recommandations intelligentes",
            "Trouvez vos plats préférés"
        ],
        internationalHeading: "Découvrez la cuisine internationale",
        internationalTag: "LA CUISINE SANS FRONTIÈRES",
        internationalText: "Des menus spéciaux pour les visiteurs du monde entier.",
        cuisines: [
            "Cuisine italienne", "Pizza, pâtes et spécialités italiennes.",
            "Cuisine japonaise", "Découvrez les sushis et les nouilles.",
            "Cuisine indienne", "Découvrez les saveurs traditionnelles indiennes.",
            "Cuisine continentale", "Profitez des plats continentaux populaires."
        ],
        restaurantTag: "DÉCOUVREZ NOS RESTAURANTS",
        restaurantHeading: "Restaurants populaires",
        restaurantText: "Trouvez votre restaurant préféré et découvrez de délicieux plats.",
        restaurants: [
            "Bistrot italien", "Italien · Continental",
            "La Maison des Épices", "Indien · Nord indien",
            "Restaurant Sushi", "Japonais · Sushi",
            "Burger Hub", "Restauration rapide · Burgers"
        ],
        viewAll: "Voir tous les restaurants →",
        footerTagline: "Bonne cuisine. Bonne humeur.",
        footerDescription: "Découvrez des restaurants, explorez les cuisines et commandez facilement.",
        footerHeadings: ["Liens rapides", "Assistance", "Contactez-nous", "Suivez-nous"],
        footerLinks: [
            "Accueil", "Restaurants", "À propos", "Menus spéciaux", "Contact",
            "FAQ", "Centre d'aide", "Conditions générales", "Confidentialité"
        ],
        location: "📍 New Delhi, Inde",
        copyright: "© 2026 SmartDine. Tous droits réservés.",
        footerLove: "Fait avec ❤️ pour les gourmands"
    },

    es: {
        nav: ["Inicio", "Restaurantes", "Nosotros", "Contacto", "Ofertas"],
        heroTag: "✦ COCINA GLOBAL, SABOR LOCAL",
        heroTitle: "Descubre comida increíble|De múltiples restaurantes",
        heroText: "Explora los mejores restaurantes, descubre menús especiales para visitantes internacionales y pide tu comida favorita con SmartDine.",
        heroButtons: ["Explorar restaurantes →", "Más información"],
        stats: ["Múltiples", "Restaurantes", "6 idiomas", "Soporte multilingüe", "Inteligente", "Experiencia gastronómica"],
        quick: [
            "Menú especial para visitantes",
            "Descubre cocinas internacionales",
            "Soporte multilingüe",
            "Cambia de idioma",
            "Seguimiento de pedidos",
            "Consulta tu pedido",
            "Recomendaciones inteligentes",
            "Encuentra tus platos favoritos"
        ],
        internationalHeading: "Explora la cocina internacional",
        internationalTag: "COMIDA SIN FRONTERAS",
        internationalText: "Menús especiales para visitantes de todo el mundo.",
        cuisines: [
            "Cocina italiana", "Pizza, pasta y deliciosos platos italianos.",
            "Cocina japonesa", "Descubre sushi y fideos japoneses.",
            "Cocina india", "Descubre los sabores tradicionales de la India.",
            "Cocina continental", "Disfruta de platos continentales populares."
        ],
        restaurantTag: "EXPLORA NUESTROS RESTAURANTES",
        restaurantHeading: "Restaurantes populares",
        restaurantText: "Encuentra tu restaurante favorito y descubre algo delicioso.",
        restaurants: [
            "Bistró italiano", "Italiano · Continental",
            "La Casa de las Especias", "Indio · Norte de India",
            "Lugar de Sushi", "Japonés · Sushi",
            "Burger Hub", "Comida rápida · Hamburguesas"
        ],
        viewAll: "Ver todos los restaurantes →",
        footerTagline: "Buena comida. Buen humor.",
        footerDescription: "Descubre restaurantes, explora cocinas y disfruta de pedidos inteligentes.",
        footerHeadings: ["Enlaces rápidos", "Ayuda", "Contáctanos", "Síguenos"],
        footerLinks: [
            "Inicio", "Restaurantes", "Nosotros", "Menús especiales", "Contacto",
            "Preguntas frecuentes", "Centro de ayuda", "Términos y condiciones", "Privacidad"
        ],
        location: "📍 Nueva Delhi, India",
        copyright: "© 2026 SmartDine. Todos los derechos reservados.",
        footerLove: "Hecho con ❤️ para los amantes de la comida"
    },

    de: {
        nav: ["Startseite", "Restaurants", "Über uns", "Kontakt", "Angebote"],
        heroTag: "✦ WELTWEITE KÜCHE, LOKALER GENUSS",
        heroTitle: "Entdecke fantastisches Essen|Aus verschiedenen Restaurants",
        heroText: "Entdecke tolle Restaurants, spezielle Menüs für internationale Gäste und bestelle dein Lieblingsessen mit SmartDine.",
        heroButtons: ["Restaurants entdecken →", "Mehr erfahren"],
        stats: ["Viele", "Restaurants", "6 Sprachen", "Mehrsprachiger Support", "Smart", "Genusserlebnis"],
        quick: [
            "Spezielle Menüs für Gäste",
            "Internationale Küche entdecken",
            "Mehrsprachiger Support",
            "Sprache wechseln",
            "Bestellverfolgung",
            "Bestellstatus ansehen",
            "Smarte Empfehlungen",
            "Lieblingsgerichte finden"
        ],
        internationalHeading: "Internationale Küche entdecken",
        internationalTag: "ESSEN OHNE GRENZEN",
        internationalText: "Besondere Menüs für Gäste aus aller Welt.",
        cuisines: [
            "Italienische Küche", "Pizza, Pasta und italienische Spezialitäten.",
            "Japanische Küche", "Entdecke Sushi und japanische Nudeln.",
            "Indische Küche", "Traditionelle indische Aromen entdecken.",
            "Kontinentale Küche", "Beliebte kontinentale Gerichte genießen."
        ],
        restaurantTag: "UNSERE RESTAURANTS ENTDECKEN",
        restaurantHeading: "Beliebte Restaurants",
        restaurantText: "Finde dein Lieblingsrestaurant und entdecke leckere Gerichte.",
        restaurants: [
            "Italienisches Bistro", "Italienisch · Kontinental",
            "Das Gewürzhaus", "Indisch · Nordindisch",
            "Sushi Restaurant", "Japanisch · Sushi",
            "Burger Hub", "Fast Food · Burger"
        ],
        viewAll: "Alle Restaurants ansehen →",
        footerTagline: "Gutes Essen. Gute Laune.",
        footerDescription: "Entdecke Restaurants, Küchen und ein intelligentes Bestellerlebnis.",
        footerHeadings: ["Schnellzugriff", "Hilfe", "Kontakt", "Folge uns"],
        footerLinks: [
            "Startseite", "Restaurants", "Über uns", "Spezialmenüs", "Kontakt",
            "FAQ", "Hilfezentrum", "Nutzungsbedingungen", "Datenschutz"
        ],
        location: "📍 Neu-Delhi, Indien",
        copyright: "© 2026 SmartDine. Alle Rechte vorbehalten.",
        footerLove: "Mit ❤️ für Feinschmecker gemacht"
    },

    ja: {
        nav: ["ホーム", "レストラン", "私たちについて", "お問い合わせ", "オファー"],
        heroTag: "✦ 世界の料理を、あなたの街で",
        heroTitle: "おいしい料理を発見|さまざまなレストランから",
        heroText: "人気のレストランを探し、海外のお客様向けの特別メニューを楽しみ、SmartDineでお気に入りの料理を注文しましょう。",
        heroButtons: ["レストランを見る →", "詳しく見る"],
        stats: ["多数の", "レストラン", "6言語", "多言語サポート", "スマート", "食事体験"],
        quick: [
            "海外のお客様向け特別メニュー",
            "世界の料理を発見",
            "多言語サポート",
            "言語を切り替える",
            "注文追跡",
            "注文状況を確認",
            "スマートなおすすめ",
            "お気に入りの料理を発見"
        ],
        internationalHeading: "世界の料理を楽しむ",
        internationalTag: "国境を越えた食体験",
        internationalText: "世界中のお客様のための特別な料理とメニュー。",
        cuisines: [
            "イタリア料理", "ピザ、パスタなどのイタリア料理。",
            "日本料理", "寿司、麺類、日本の料理を楽しむ。",
            "インド料理", "伝統的なインドの味を発見。",
            "各国料理", "人気の各国料理を楽しみましょう。"
        ],
        restaurantTag: "レストランを探す",
        restaurantHeading: "人気のレストラン",
        restaurantText: "お気に入りのレストランでおいしい料理を見つけましょう。",
        restaurants: [
            "イタリアンビストロ", "イタリア料理 · 各国料理",
            "スパイスハウス", "インド料理",
            "寿司レストラン", "日本料理 · 寿司",
            "バーガーハブ", "ファストフード · バーガー"
        ],
        viewAll: "すべてのレストランを見る →",
        footerTagline: "おいしい料理。楽しい時間。",
        footerDescription: "レストランや世界の料理を発見し、スマートに注文しましょう。",
        footerHeadings: ["クイックリンク", "サポート", "お問い合わせ", "フォローする"],
        footerLinks: [
            "ホーム", "レストラン", "私たちについて", "特別メニュー", "お問い合わせ",
            "よくある質問", "ヘルプセンター", "利用規約", "プライバシーポリシー"
        ],
        location: "📍 インド、ニューデリー",
        copyright: "© 2026 SmartDine. All Rights Reserved.",
        footerLove: "食を愛する人のために ❤️"
    }
};

// HELPER FUNCTION
function setTexts(selector, values) {
    const elements = document.querySelectorAll(selector);

    elements.forEach((element, index) => {
        if (values[index] !== undefined) {
            element.textContent = values[index];
        }
    });
}

// APPLY SELECTED LANGUAGE
function changeLanguage(language) {

    const t = translations[language] || translations.en;

    document.documentElement.lang = language;

    // Navbar desktop and mobile
    setTexts(".nav-links a", t.nav);
    setTexts(".mobile-menu > a:nth-child(-n+5)", t.nav);

    // Login and signup
    setTexts(".nav-actions .login-btn", ["Login"]);
    setTexts(".nav-actions .signup-btn", ["Sign Up"]);

    // Hero
    setTexts(".hero-tag", [t.heroTag]);

    const heroTitle = document.querySelector(".hero-content h1");
    if (heroTitle) {
        const parts = t.heroTitle.split("|");
        heroTitle.innerHTML = `${parts[0]}<span>${parts[1]}</span>`;
    }

    setTexts(".hero-content > p", [t.heroText]);
    setTexts(".hero-buttons a", t.heroButtons);
    setTexts(".stat-item strong, .stat-item span", t.stats);

    // Quick features
    setTexts(".quick-feature-card h3, .quick-feature-card p", t.quick);

    // International cuisine
    setTexts(".international-section .section-heading span", [t.internationalTag]);
    setTexts(".international-section .section-heading h2", [t.internationalHeading]);
    setTexts(".international-section .section-heading p", [t.internationalText]);
    setTexts(".international-card h3, .international-card p", t.cuisines);

    // Restaurants
    setTexts(".restaurants-section .section-heading span", [t.restaurantTag]);
    setTexts(".restaurants-section .section-heading h2", [t.restaurantHeading]);
    setTexts(".restaurants-section .section-heading p", [t.restaurantText]);
    setTexts(".restaurant-info h3, .restaurant-info p", t.restaurants);
    setTexts(".view-all a", [t.viewAll]);

    // Footer
    setTexts(".footer-brand > p:first-of-type", [t.footerTagline]);
    setTexts(".brand-description", [t.footerDescription]);
    setTexts(".footer-column h3", t.footerHeadings);

    const footerLinks = document.querySelectorAll(".footer-column a:not(.social-links a)");
    footerLinks.forEach((link, index) => {
        if (t.footerLinks[index] !== undefined) {
            link.textContent = t.footerLinks[index];
        }
    });

    setTexts(".contact-column p", [t.location]);
    setTexts(".footer-bottom p", [t.copyright, t.footerLove]);

    // Sync both dropdowns
    if (languageSelect) languageSelect.value = language;
    if (mobileLanguageSelect) mobileLanguageSelect.value = language;

    // Save selected language during this browser session
    try {
        sessionStorage.setItem("smartdine-language", language);
    } catch (error) {
        console.warn("Language preference could not be saved.");
    }
}

// DESKTOP LANGUAGE SELECT
if (languageSelect) {
    languageSelect.addEventListener("change", function () {
        changeLanguage(this.value);
    });
}

// MOBILE LANGUAGE SELECT
if (mobileLanguageSelect) {
    mobileLanguageSelect.addEventListener("change", function () {
        changeLanguage(this.value);
    });
}

// LOAD SAVED LANGUAGE
let savedLanguage = "en";

try {
    savedLanguage = sessionStorage.getItem("smartdine-language") || "en";
} catch (error) {
    savedLanguage = "en";
}

changeLanguage(savedLanguage);
