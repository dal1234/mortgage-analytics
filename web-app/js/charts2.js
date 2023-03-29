var quarterly_repurchase = d3.csv("../../data/repurchase_qtr_curves_recent.csv?t=${Date.now()}");
var quarterly_repurchase_rates = d3.csv("../../data/quarterly_trailing_repurchase.csv?t=${Date.now()}");
var counts_by_quarter = d3.csv("../../data/repurchase_count_by_quarter.csv?t=${Date.now()}");


quarterly_repurchase.then(function (data) {
    makeQtrLineChart(data)
});

quarterly_repurchase_rates.then(function (data) {
    makeQtrBarChart(data)
});

counts_by_quarter.then(function (data) {
    makeQtrCountBarChart(data, 'counts_by_qtr')
});


function makeQtrLineChart(data) {

    const unique = [...new Set(data.map(item => item.ORIG_QUARTER))];

    function filteredData2(value) {
        var filterdata = data.filter(function (d, i) {
            if (d['ORIG_QUARTER'] == value) {
                return d;
            }
        })
        return filterdata
    }

    chart_data = []

    for (var i = 0; i < unique.length; i++) {
        vintage_data = filteredData2(unique[i])
        var LOAN_AGE = [],
            repurch_rate = [];
        vintage_data.map(function (d) {
            LOAN_AGE.push(d.LOAN_AGE_QTR);
            repurch_rate.push(d.cum_repurchase_rate);
        })
        var result = {
            x: LOAN_AGE,
            y: repurch_rate,
            type: 'scatter',
            mode: 'lines',
            name: unique[i]
        };
        chart_data.push(result);

    }

    var layout = {
        title: {
            text: 'Quarterly cumulative repurchase rates'
        }
    }

    Plotly.newPlot('quarterly_line', chart_data, layout);
}


function makeQtrBarChart(data) {
    var REPURCHASE_QUARTER = [],
        qtr8 = [],
        qtr10 = [],
        qtr12 = [];
    data.map(function (d) {
        REPURCHASE_QUARTER.push(d.REPURCHASE_QUARTER);
        qtr8.push(d.qtr8);
        qtr10.push(d.qtr10);
        qtr12.push(d.qtr12)
    })

    var config = { responsive: true };

    var trace1 = {
        x: REPURCHASE_QUARTER,
        y: qtr8,
        type: 'bar',
        name: 'Trailing 8 quarters'
    }

    var trace2 = {
        x: REPURCHASE_QUARTER,
        y: qtr10,
        type: 'bar',
        name: 'Trailing 10 quarters'
    }

    var trace3 = {
        x: REPURCHASE_QUARTER,
        y: qtr12,
        type: 'bar',
        name: 'Trailing 12 quarters'
    }

    var data = [trace1, trace2, trace3];

    var layout = {
        title: {
            text: 'Repurchase rate by n-month trailing quarters of originations (% of originations)'
        },
        barmode: 'group',
        legend: { "orientation": "h" },
        annotations: [
            {
                x: -.09,
                y: -.3,
                xref: 'x domain',
                yref: 'y domain',
                text: 'Note: Includes repurchases occuring during the quarter for loans originated during the trailing n months.',
                showarrow: false
            }
        ]
        // width: 1000,
        // height: 500
    };

    TESTER = document.getElementById('quarterly_bar');
    Plotly.newPlot(TESTER, data, layout, config);

};