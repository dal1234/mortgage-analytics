function makeQtrCountBarChart(data, element_id) {
    var REPURCHASE_QUARTER = [],
        counts = [];
    data.map(function (d) {
        REPURCHASE_QUARTER.push(d.REPURCHASE_QUARTER);
        counts.push(d.LOAN_COUNT);
    })

    var config = { responsive: true };

    var trace1 = {
        x: REPURCHASE_QUARTER,
        y: counts,
        type: 'bar'
    }

    var data = [trace1];

    var layout = {
        title: {
            text: 'Repurchase count by quarter'
        }
        // width: 1000,
        // height: 500
    };

    TESTER = document.getElementById(element_id);
    Plotly.newPlot(TESTER, data, layout, config);

};