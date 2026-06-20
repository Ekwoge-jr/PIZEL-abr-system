import broker from "./broker.js";
import { buildState } from "./state_builder.js";
import { updateLastAction } from "./state_builder.js";
import { selectAction } from "./policy.js";


let latestNetwork = null;
let latestROI = null;


broker.subscribe(
    "network_metrics",
    (data) => {

        latestNetwork = data;

        evaluate();
    }
);


broker.subscribe(
    "roi_metrics",
    (data) => {

        latestROI = data;

        
        //evaluate();
    }
);





async function evaluate() {

    if(!latestNetwork)
        return;


    /// metric state
    const state = buildState( latestNetwork );

    const action = await selectAction(state);

    updateLastAction(action);


    console.log(
        "RL STATE",
        state
    );


    console.log(
        "ACTION:",
        action
    )


    // Publish decision, so that dash.js can use it
    broker.publish(
        "bitrate_decision",
        { 
            representation: action
        }
    );


}