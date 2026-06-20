/// collects the roi metrics from the server 
/// and uses the broker to publish it for all subscribers to use
/// the file executes every 2 seconds

import broker from "./broker.js"

async function fetchROIMetrics() {

    try {

        const response = await fetch(
            "http://localhost:5000/api/roi/metrics"
        );

        const metrics = await response.json();

        broker.publish(
            "roi_metrics",
            metrics
        );

    }
    catch(error) {

        console.error(
            "ROI Metrics Error:",
            error
        );
    }
}


setInterval(
    fetchROIMetrics,
    2000
);