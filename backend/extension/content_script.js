// ✅ Confirm script is injected
console.log("✅ Content script loaded");

// 🔍 Price extraction function
function getPrice() {
    const selectors = [
        // Amazon specific
        ".a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-price-whole",

        // Generic fallbacks
        "[class*='price']",
        "[id*='price']"
    ];

    for (let selector of selectors) {
        let element = document.querySelector(selector);

        if (element) {
            let text = element.innerText || element.textContent;

            if (text) {
                let cleaned = text.replace(/[^0-9.]/g, "");
                if (cleaned.length > 0) {
                    console.log(`💰 Price found using ${selector}:`, cleaned);
                    return cleaned;
                }
            }
        }
    }

    console.log("❌ Price not found");
    return null;
}

// 📩 Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    if (request.action === "GET_PRICE") {

        console.log("📩 Message received from popup");

        const price = getPrice();

        sendResponse({
            price: price
        });
    }

});