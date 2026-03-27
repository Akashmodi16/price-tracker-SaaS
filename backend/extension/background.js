// Run every 4 hours
chrome.alarms.create("priceCheck", { periodInMinutes: 240 });

// Listen for alarm
chrome.alarms.onAlarm.addListener(async (alarm) => {
    if (alarm.name === "priceCheck") {
        chrome.storage.local.get("trackedItems", async (data) => {
            let items = data.trackedItems || [];

            for (let item of items) {
                try {
                    let response = await fetch(item.url);
                    let text = await response.text();

                    let doc = new DOMParser().parseFromString(text, "text/html");

                    let priceElement =
                        doc.querySelector("[class*='price']") ||
                        doc.querySelector("[id*='price']");

                    if (priceElement) {
                        let newPrice = priceElement.innerText.replace(/[^0-9.]/g, "");

                        if (newPrice < item.price) {
                            chrome.notifications.create({
                                type: "basic",
                                iconUrl: "icon.png",
                                title: "Price Dropped!",
                                message: `New price: ₹${newPrice}`
                            });
                        }
                    }
                } catch (err) {
                    console.log("Error fetching:", err);
                }
            }
        });
    }
});