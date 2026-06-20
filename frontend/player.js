// player.js — FULLY CORRECTED VERSION


import broker from "./broker.js";
import {
    incrementChunkCounter
} from "./state_builder.js";

const video =
    document.getElementById(
        "videoPlayer"
    );

video.muted = true;

const url =
    "http://localhost:5000/api/dash/manifest.mpd";

const player =
    dashjs.MediaPlayer().create();

player.initialize(
    video,
    url,
    true
);

console.log(
    "DASH Player Initialized"
);



player.on(
    dashjs.MediaPlayer.events.STREAM_INITIALIZED,
    () => {

        const dashMetrics =
            player.getDashMetrics();

        const buffer = Math.max(
            dashMetrics.getCurrentBufferLevel(
                "video"
            ),
            5
        );

        console.log(
            "Initial buffer:",
            buffer
        );

        player.updateSettings({
            streaming: {
                abr: {
                    autoSwitchBitrate: {
                        video: false
                    }
                }
            }
        });
    }
);


/**
 * Trigger metrics generation
 * whenever a segment finishes.
 */
player.on(
    dashjs.MediaPlayer.events.FRAGMENT_LOADING_COMPLETED,
    (e) => {

        console.log("Dash.js version:", player.getVersion());


        if (
            !e.request ||
            e.request.type !== "MediaSegment"
        ) {
            return;
        }

        const req = e.request;

        incrementChunkCounter();

        const dashMetrics =
            player.getDashMetrics();

        const buffer =
            dashMetrics.getCurrentBufferLevel(
                "video"
            );

        /*const throughput =
            player.getAverageThroughput(
                "video"
            );*/

    
        const bitrate = req.bandwidth || 300000;
        
        

        let downloadTime = 0;

        if (
            req.startDate &&
            req.endDate
        ) {
            downloadTime =
                (req.endDate.getTime() -
                 req.startDate.getTime()) / 1000;
            
        }



        let throughputBps = 0;

        if (req.trace && req.trace.length > 0 && downloadTime > 0) {
            const bytesDownloaded = req.trace.reduce((sum, t) => {
                if (Array.isArray(t.b)) {
                    return sum + t.b.reduce((s, x) => s + x, 0);
                }
                return sum + (t.b || 0);
            }, 0);

            throughputBps = (bytesDownloaded * 8) / downloadTime;

            console.log("Bytes downloaded:", bytesDownloaded);
        } else {
            // Fallback to dash.js's average if trace data
            // is unavailable for any reason
            throughputBps = player.getAverageThroughput("video");
            console.warn("No trace data — falling back to dash.js average");
        }



        console.log(
            "================================"
        );

        //console.log(req)
        //console.log("trequest =", req.trequest)
        //console.log("tfinish =", req.tfinish)
        //console.log("REQUEST OBJECT", e.request);

        console.log(
            "SEGMENT COMPLETED"
        );

        console.log(
            "URL:",
            req.url
        );

        console.log(
            "Buffer:",
            buffer
        );

        console.log(
            "Throughput:",
            //throughput 
            throughputBps
        );

        console.log(
            "Download Time:",
            downloadTime
        );

        console.log(
            "Bitrate:",
            bitrate
        );



        broker.publish(
            "network_metrics",
            {
                buffer,
                bitrate,
                throughput: throughputBps,
                downloadTime
            }
        );
    }
);


broker.subscribe(
    "bitrate_decision",
    (data) => {

        player.setRepresentationForTypeByIndex(
            "video",
            data.representation
        );

        console.log(
            "Switching to representation:",
            data.representation
        );
    }
);


player.on(
    dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED,
    (e) => {

        console.log(
            "Quality switched"
        );


        console.log(
            "Old Representation:",
            e.oldRepresentation
        );

        console.log(
            "New Representation:",
            e.newRepresentation
        );

        console.log(e);
    }
);






















/* // claude code
import broker from "./broker.js";
import { incrementChunkCounter } from "./state_builder.js";

const video = document.getElementById("videoPlayer");

video.muted = true;

const url = "http://localhost:5000/api/dash/manifest.mpd";

const player = dashjs.MediaPlayer().create();

player.initialize(video, url, true);


// ── FIX 1: Force playback to resume after browser power-saving
//           pauses (Chromium pauses video-only background media) ──
function ensurePlaying() {
    const playPromise = video.play();
    if (playPromise !== undefined) {
        playPromise.catch((err) => {
            console.warn("play() failed, retrying in 500ms:", err.message);
            setTimeout(ensurePlaying, 500);
        });
    }
}

document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && video.paused) {
        console.log("Tab visible again — resuming playback");
        ensurePlaying();
    }
});

video.addEventListener("pause", () => {
    console.warn("Video paused unexpectedly. visibility=",
        document.visibilityState);
    if (document.visibilityState === "visible") {
        ensurePlaying();
    }
});


player.on(
    dashjs.MediaPlayer.events.STREAM_INITIALIZED,
    () => {
        const dashMetrics = player.getDashMetrics();
        let buffer = Math.max(
            dashMetrics.getCurrentBufferLevel("video"),
            5
        );
        console.log("Initial buffer:", buffer);

        player.updateSettings({
            streaming: {
                abr: {
                    autoSwitchBitrate: {
                        video: false
                    }
                }
            }
        });

        ensurePlaying();
    }
);


// ── Track the URL of the last segment we already reported,
//    so we always pick up a genuinely NEW completed segment ──
let lastReportedUrl = null;


setInterval(() => {

    const dashMetrics = player.getDashMetrics();

    const buffer = dashMetrics.getCurrentBufferLevel("video");

    let bitrate = 300000;
    const rep = dashMetrics.getCurrentRepresentationSwitch("video", true);
    if (rep) bitrate = rep.bitrate;

    const requests = dashMetrics.getHttpRequests("video");

    const mediaRequests = requests.filter(
        r => r.type === "MediaSegment"
    );

    let throughputBps = 0;
    let downloadTime  = 0;

    // FIX 2: Require trequest/tfinish to be valid AND that
    //        this segment hasn't already been reported.
    const completedRequests = mediaRequests.filter(
        r => r.trequest && r.tfinish && r.url !== lastReportedUrl
    );

    console.log("Total media requests:", mediaRequests.length);
    console.log("New completed requests:", completedRequests.length);

    if (completedRequests.length > 0) {

        const last = completedRequests[completedRequests.length - 1];

        console.log("Segment URL:", last.url);
        console.log("trequest (raw):", last.trequest);
        console.log("tfinish  (raw):", last.tfinish);

        // FIX 3: Explicitly coerce to numeric epoch ms via
        //        new Date(...).getTime(), which is robust
        //        whether trequest/tfinish are Date objects
        //        or ISO strings.
        const tStart = new Date(last.trequest).getTime();
        const tEnd   = new Date(last.tfinish).getTime();

        console.log("tStart (ms):", tStart, "| tEnd (ms):", tEnd);

        if (!isNaN(tStart) && !isNaN(tEnd) && tEnd > tStart) {
            downloadTime = (tEnd - tStart) / 1000;
        } else {
            console.warn(
                "Invalid or zero-duration timestamps — "
                + "tStart/tEnd did not produce a valid positive delta."
            );
        }

        // FIX 4: Compute throughput from actual bytes transferred,
        //        not from dash.js's cached average.
        let bytesDownloaded = 0;

        if (last.trace && last.trace.length > 0) {
            bytesDownloaded = last.trace.reduce(
                (sum, t) => {
                    if (Array.isArray(t.b)) {
                        return sum + t.b.reduce((s, x) => s + x, 0);
                    }
                    return sum + (t.b || 0);
                },
                0
            );
        } else {
            console.warn("No trace data on this request — "
                + "trace array is missing or empty.");
        }

        console.log("Bytes downloaded:", bytesDownloaded);

        if (downloadTime > 0 && bytesDownloaded > 0) {
            throughputBps = (bytesDownloaded * 8) / downloadTime;
        }

        lastReportedUrl = last.url;
    }

    console.log("DOWNLOAD TIME:", downloadTime);
    console.log("Throughput Mbps:", throughputBps / 1_000_000);

    broker.publish("network_metrics", {
        buffer,
        bitrate,
        throughput: throughputBps,
        downloadTime
    });

}, 2000);


broker.subscribe(
    "bitrate_decision",
    (data) => {
        player.setRepresentationForTypeByIndex(
            "video",
            data.representation
        );
        console.log("Switching to representation:", data.representation);
    }
);


player.on(
    dashjs.MediaPlayer.events.FRAGMENT_LOADING_COMPLETED,
    (e) => {
        if (e.request.type === "MediaSegment") {
            incrementChunkCounter();
        }
    }
);


player.on(
    dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED,
    (e) => {
        incrementChunkCounter();
        console.log("Quality switched");
        console.log("Old:", e.oldQuality);
        console.log("New:", e.newQuality);
        console.log(e);
    }
);


console.log("DASH Player Initialized");
*/














/** 
import broker from "./broker.js";
import { incrementChunkCounter } from "./state_builder.js";

const video = document.getElementById( "videoPlayer" );

video.muted = true;

const url =
    "http://localhost:5000/api/dash/manifest.mpd";

const player =
    dashjs.MediaPlayer().create();

player.initialize(
    video,
    url,
    true
);



player.on(
    dashjs.MediaPlayer.events.STREAM_INITIALIZED,
    () => {
        const dashMetrics = player.getDashMetrics();
        let buffer = Math.max(
            dashMetrics.getCurrentBufferLevel("video"),
            5
        );
        console.log("Initial buffer:", buffer);

        player.updateSettings({
            streaming: {
                abr: {
                    autoSwitchBitrate: {
                        video: false
                    }
                }
            }
        });

    }
);





setInterval(() => {

    

    const dashMetrics =
        player.getDashMetrics();

    const buffer =
        dashMetrics.getCurrentBufferLevel(
            "video"
        );

    const throughput =
        player.getAverageThroughput(
            "video"
        );

    console.log(
        player.getAverageThroughput(
            "video"
        )
    )

    let bitrate = 300000;

    const rep =
        dashMetrics.getCurrentRepresentationSwitch(
            "video",
            true
        );

    if(rep)
        bitrate = rep.bitrate;


    let downloadTime = 0;

    const requests =
        dashMetrics.getHttpRequests(
            "video"
        );


    const mediaRequests = 
        requests.filter(
            r => r.type === "MediaSegment"
        );
    

    if(mediaRequests.length > 0){

        
        const completedRequests =
            mediaRequests.filter(
                r => r.trequest && r.tfinish
            );

        if(completedRequests.length > 0){

            const last =
                completedRequests[
                    completedRequests.length - 1
                ];

            console.log(last);
            console.log("trequest:", last.trequest);
            console.log("tfinish:", last.tfinish);
            console.log(completedRequests.at(-1));

            downloadTime =
                (last.tfinish - last.trequest) / 1000;
        }  

        
    }




    console.log(requests);
    console.log(requests.map(r => r.type));


    console.log("DOWNLOAD TIME:", downloadTime)

    console.log(
        "Mbps:",
        throughput / 1000
        )

    broker.publish(
        "network_metrics",
        {
            buffer,
            bitrate,
            throughput: throughput ,
            downloadTime
        }
    );

}, 2000);



broker.subscribe(
    "bitrate_decision",
    (data) => {

        player.setRepresentationForTypeByIndex(
            "video",
            data.representation
        );

        console.log(
            "Switching to representation:",
            data.representation
        );

    }
);


player.on(
    dashjs.MediaPlayer.events.FRAGMENT_LOADING_COMPLETED,
    (e) => {

        if(e.request.type === "MediaSegment"){
            incrementChunkCounter();
        }

    }
);



player.on(
    dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED,
    (e) => {

        incrementChunkCounter();

        console.log("Quality switched");

        console.log("Old:", e.oldQuality);

        console.log("New:", e.newQuality);

        console.log(e);

    }
);


console.log("DASH Player Initialized");
*/




























/** 
const video = document.getElementById( "videoPlayer" );

video.muted = true; // allows autoplay without user interaction


const url = "http://localhost:5000/api/dash/manifest.mpd";

const player = dashjs.MediaPlayer().create();

player.initialize(

    video,

    url,

    true

);



setInterval(() => {

    const dashMetrics =
        player.getDashMetrics();

    const streamInfo =
        player.getActiveStream().getStreamInfo();

    const buffer =
        dashMetrics.getCurrentBufferLevel(
            "video"
        );

    //const bitrate =
    //    player.getCurrentTrackFor("video");



    // Get the current quality index
    const qualityIndex = player.getCurrentTrackFor("video");

    // Get bitrate for that quality index
    const bitrate = dashMetrics.getCurrentRepresentationSwitch("video", true).bitrate;

    

    const throughput =
        player.getAverageThroughput(
            "video"
        );

    broker.publish(
        "network_metrics",
        {
            buffer,

            bitrate,

            throughput
        }
    );

    
}, 2000);



/// listening to the broker
broker.subscribe(
    "bitrate_decision",
    (data) => {

        player.setRepresentationForTypeByIndex(
            "video",
            data.representation
            
        );

        console.log(
            "Switching to",
            data.representation
        );

    }
);




player.on(
    dashjs.MediaPlayer.events.STREAM_INITIALIZED,
    () => {

        player.updateSettings({
            streaming: {
                abr: {
                    autoSwitchBitrate: {
                        video: false
                    }
                }
            }
        });

    }
);


player.on(
    dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED,
    (e) => {

        console.log("Quality switched");

        console.log("Old:", e.oldQuality);
        console.log("New:", e.newQuality);

    }
);


console.log( "DASH Player Initialized" );
*/