// roi_debug.js

import broker from "./broker.js";


broker.subscribe(
    "network_metrics",
    (data) => {

        console.log(
            "Network Metrics:",
            data
        );

    }
);


/** 
broker.subscribe(
    "roi_metrics",
    (data) => {

        console.log(
            "ROI Metrics:",
            data
        );

    }
);
*/