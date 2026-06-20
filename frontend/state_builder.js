/// A State Builder is a structural pattern whose sole job is to 
// capture messy, asynchronous raw data streams from different parts of your system 
// and assemble them into a single, synchronized vector (or dictionary) that your AI model can read


// state_builder.js

const HISTORY_LEN = 5;

const throughputHistory = [];
const downloadHistory = [];

const MAX_THROUGHPUT_BPS = 8_000_000; 
const MAX_DOWNLOAD_TIME_S = 16.0;
const BUFFER_MAX_S = 60.0;
const MAX_CHUNKS = 48;

let chunkCounter = 0;
let lastAction = 1;

export function updateLastAction(action) {
    lastAction = action;
}

export function incrementChunkCounter() {
    chunkCounter++;
}

export function buildState(network) {

    const throughput =
        Number.isFinite(network.throughput)
            ? network.throughput
            : 0;

    const downloadTime =
        Number.isFinite(network.downloadTime)
            ? network.downloadTime
            : 0;

    throughputHistory.push(throughput);
    downloadHistory.push(downloadTime);

    if (throughputHistory.length > HISTORY_LEN)
        throughputHistory.shift();

    if (downloadHistory.length > HISTORY_LEN)
        downloadHistory.shift();

    while (throughputHistory.length < HISTORY_LEN)
        throughputHistory.unshift(
            throughputHistory[0] || 0
        );

    while (downloadHistory.length < HISTORY_LEN)
        downloadHistory.unshift(
            downloadHistory[0] || 0
        );

    const thNorm = throughputHistory.map(
        t => Math.min(
            t / MAX_THROUGHPUT_BPS,
            1.0
        )
    );

    const dlNorm = downloadHistory.map(
        d => Math.min(
            d / MAX_DOWNLOAD_TIME_S,
            1.0
        )
    );

    const bufferNorm = Math.min(
        network.buffer / BUFFER_MAX_S,
        1.0
    );

    const remainingNorm = Math.max(
        0,
        (MAX_CHUNKS - chunkCounter) / MAX_CHUNKS
    );

    const bitrateLadder = [
        300000,
        800000,
        1500000
    ];

    const lastBitrateNorm =
        bitrateLadder[lastAction] /
        bitrateLadder[2];

    const oneHot = [0, 0, 0];
    oneHot[lastAction] = 1;

    return [
        ...thNorm,
        ...dlNorm,
        bufferNorm,
        remainingNorm,
        lastBitrateNorm,
        ...oneHot
    ];
}















/* // claude code
const HISTORY_LEN = 5;

const throughputHistory = [];
const downloadHistory = [];

const MAX_THROUGHPUT_BPS = 8_000_000;
const MAX_DOWNLOAD_TIME_S = 16.0;
const BUFFER_MAX_S = 60.0;
const MAX_CHUNKS = 48;

let chunkCounter = 0;
let lastAction = 1;


export function updateLastAction(action) {
    lastAction = action;
}


export function incrementChunkCounter() {
    chunkCounter++;
}


export function buildState(network) {

    throughputHistory.push(network.throughput);
    if (throughputHistory.length > HISTORY_LEN)
        throughputHistory.shift();

    downloadHistory.push(network.downloadTime);
    if (downloadHistory.length > HISTORY_LEN)
        downloadHistory.shift();

    while (throughputHistory.length < HISTORY_LEN)
        throughputHistory.unshift(throughputHistory[0] || 0);

    while (downloadHistory.length < HISTORY_LEN)
        downloadHistory.unshift(downloadHistory[0] || 0);

    const thNorm = throughputHistory.map(
        t => Math.min(t / MAX_THROUGHPUT_BPS, 1.0)
    );

    const dlNorm = downloadHistory.map(
        d => Math.min(d / MAX_DOWNLOAD_TIME_S, 1.0)
    );

    const bufferNorm = Math.min(network.buffer / BUFFER_MAX_S, 1.0);

    // FIX: wraparound so long-running live sessions (beyond
    // 48 chunks, ~4.8 minutes) don't permanently flatline at 0,
    // which would push the agent into an out-of-distribution
    // state it never saw during training.
    const effectiveChunkPosition = chunkCounter % MAX_CHUNKS;

    const remainingNorm = Math.max(
        0,
        (MAX_CHUNKS - effectiveChunkPosition) / MAX_CHUNKS
    );

    const bitrateLadder = [300000, 800000, 1500000];

    const lastBitrateNorm = bitrateLadder[lastAction] / bitrateLadder[2];

    const oneHot = [0, 0, 0];
    oneHot[lastAction] = 1;

    console.log("RAW THROUGHPUT:", network.throughput);
    console.log("NORMALIZED:", network.throughput / MAX_THROUGHPUT_BPS);

    return [
        ...thNorm,
        ...dlNorm,
        bufferNorm,
        remainingNorm,
        lastBitrateNorm,
        ...oneHot
    ];
}
*/

















































// state_builder.js
/** 
const HISTORY_LEN = 5;

const throughputHistory = [];
const downloadHistory = [];

const MAX_THROUGHPUT_BPS = 8_000_000;
const MAX_DOWNLOAD_TIME_S = 16.0;
const BUFFER_MAX_S = 60.0;
const MAX_CHUNKS = 48;

let chunkCounter = 0;
let lastAction = 1; // start at medium bitrate


export function updateLastAction(action) {
    lastAction = action;
}


export function incrementChunkCounter() {
    chunkCounter++;
}


export function buildState(network) {

    throughputHistory.push(network.throughput);

    if (throughputHistory.length > HISTORY_LEN)
        throughputHistory.shift();

    
    downloadHistory.push(network.downloadTime);


    if (downloadHistory.length > HISTORY_LEN)
        downloadHistory.shift();


    while (throughputHistory.length < HISTORY_LEN)
        throughputHistory.unshift(
            throughputHistory[0] || 0
        );


    while (downloadHistory.length < HISTORY_LEN)
        downloadHistory.unshift(
            downloadHistory[0] || 0
        );


    const thNorm = throughputHistory.map(
        t => Math.min(
            t / MAX_THROUGHPUT_BPS,
            1.0
        )
    );


    const dlNorm = downloadHistory.map(
        d => Math.min(
            d / MAX_DOWNLOAD_TIME_S,
            1.0
        )
    );


    const bufferNorm = Math.min(
        network.buffer / BUFFER_MAX_S,
        1.0
    );


    const remainingNorm = Math.max(
        0,
        (MAX_CHUNKS - chunkCounter) / MAX_CHUNKS
    );


    const bitrateLadder = [
        300000,
        800000,
        1500000
    ];


    const lastBitrateNorm =
        bitrateLadder[lastAction] /
        bitrateLadder[2];


    const oneHot = [0, 0, 0];
    oneHot[lastAction] = 1;

    console.log("RAW THROUGHPUT:", network.throughput);
    console.log(
        "NORMALIZED:",
        network.throughput / MAX_THROUGHPUT_BPS
    );

    return [
        ...thNorm,
        ...dlNorm,
        bufferNorm,
        remainingNorm,
        lastBitrateNorm,
        ...oneHot
    ];
}

*/


















/** 
export function buildState(
    network,
    roiScore
) {

    let bufferState;
    let roiState;

    if(network.buffer < 5)
        bufferState = "LOW";

    else if(network.buffer < 15)
        bufferState = "MEDIUM";

    else
        bufferState = "HIGH";



    if(roiScore < 10)
        roiState = "LOW";

    else if(roiScore < 30)
        roiState = "MEDIUM";

    else
        roiState = "HIGH";



    return {
        bufferState,
        roiState
    };
}
*/