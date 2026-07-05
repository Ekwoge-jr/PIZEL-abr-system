// metrics_logger.js

const sessionLog = [];

let segmentNumber = 0;

let switchCount = 0;

let rebufferCount = 0;

let totalRebufferTime = 0;

let rebufferStart = null;

const startupStart = performance.now();

let startupDelay = null;



export function recordQualitySwitch() {

    switchCount++;

}



export function initializeVideoMetrics(video) {

    video.addEventListener(
        "waiting",
        () => {

            rebufferCount++;

            rebufferStart =
                performance.now();

        }
    );



    video.addEventListener(
        "playing",
        () => {

            if (
                startupDelay === null
            ) {

                startupDelay =
                    (
                        performance.now() -
                        startupStart
                    ) / 1000;
            }



            if (
                rebufferStart !== null
            ) {

                totalRebufferTime +=
                    (
                        performance.now() -
                        rebufferStart
                    ) / 1000;

                rebufferStart = null;
            }
        }
    );
}



export function logDecisionPoint({

    throughput,
    buffer,
    downloadTime,
    bitrate,
    action

}) {

    segmentNumber++;

    sessionLog.push({

        segment: segmentNumber,

        timestamp:
            Date.now(),

        throughputMbps:
            throughput / 1000000,

        bufferSeconds:
            buffer,

        downloadTime:
            downloadTime,

        bitrateKbps:
            bitrate / 1000,

        action,

        switchCount,

        rebufferCount,

        totalRebufferTime

    });

}



export function exportSessionLog() {

    const csv = [

        "segment,timestamp,throughput_mbps,buffer_s,download_time_s,bitrate_kbps,action,switch_count,rebuffer_count,rebuffer_time_s",

        ...sessionLog.map(

            row =>

                `${row.segment},` +

                `${row.timestamp},` +

                `${row.throughputMbps.toFixed(3)},` +

                `${row.bufferSeconds.toFixed(2)},` +

                `${row.downloadTime.toFixed(3)},` +

                `${row.bitrateKbps},` +

                `${row.action},` +

                `${row.switchCount},` +

                `${row.rebufferCount},` +

                `${row.totalRebufferTime.toFixed(3)}`

        )

    ].join("\n");



    const blob =
        new Blob(
            [csv],
            { type: "text/csv" }
        );



    const url =
        URL.createObjectURL(blob);



    const a =
        document.createElement("a");

    a.href = url;

    a.download =
        `evaluation_${Date.now()}.csv`;

    a.click();

}



export function getSummary() {

    const avgBitrate =

        sessionLog.reduce(
            (sum, row) =>
                sum + row.bitrateKbps,
            0
        ) /

        sessionLog.length;



    const avgBuffer =

        sessionLog.reduce(
            (sum, row) =>
                sum + row.bufferSeconds,
            0
        ) /

        sessionLog.length;



    const avgThroughput =

        sessionLog.reduce(
            (sum, row) =>
                sum + row.throughputMbps,
            0
        ) /

        sessionLog.length;



    console.table({

        startupDelay,

        avgBitrate,

        avgBuffer,

        avgThroughput,

        switchCount,

        rebufferCount,

        totalRebufferTime

    });

}



window.exportSessionLog =
    exportSessionLog;

window.getSummary =
    getSummary;