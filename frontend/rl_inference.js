// rl_inference.js

//import * as ort from "onnxruntime-web";


let session = null;

export async function loadModel() {

    session = await ort.InferenceSession.create(
        "./model/ppo_abr_single.onnx"
    );

    console.log("PPO Loaded");
}

// prediction
export async function predict(state) {

    const input = new ort.Tensor(
        "float32",
        Float32Array.from(state),
        [1,16]
    );

    const result = await session.run({
        state: input
    });

    console.log(session.inputNames);
    console.log(session.outputNames);

    console.log(result);
    
    const logits =
        result.logits.data;


    let best = 0;

    for(let i=1;i<logits.length;i++){

        if(logits[i] > logits[best])
            best = i;
    }

    return best;
}