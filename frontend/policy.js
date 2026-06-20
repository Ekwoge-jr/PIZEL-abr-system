import { predict } from "./rl_inference.js";
import { loadModel } from "./rl_inference.js";

let modelReady = false;

(async () => {
    await loadModel();
    modelReady = true;
})();


export async function selectAction(stateVector) {

    if (!modelReady) {
        return 1; // fallback = 800kbps
    }

    return await predict(stateVector);
}


/** 
export function selectAction(state) {

    if(
        state.bufferState === "HIGH" &&
        state.roiState === "HIGH"
    ) {
        return 2;
    }

    if(
        state.bufferState === "MEDIUM"
    ) {
        return 1;
    }

    return 0;
}
*/