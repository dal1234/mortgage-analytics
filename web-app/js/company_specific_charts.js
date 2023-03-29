var counts_by_quarter_seller = d3.csv("../../data/repurchase_count_by_quarter_seller.csv?t=${Date.now()}");


counts_by_quarter_seller.then(function (data) {
    const seller_list = [...new Set(data.map(item => item.SELLER))];

    const select = document.getElementById('my_list');
    for (const item of seller_list) {
        const option = document.createElement('option');
        option.appendChild(document.createTextNode(item));
        select.appendChild(option);
    }
});


counts_by_quarter_seller.then(function (data) {
    var elem = document.getElementById('my_list');
    makeQtrCountBarChart(filteredData(elem.value), 'counts_by_seller')
    elem.addEventListener("change", onSelectChange);

    function filteredData(value) {
        var filterdata = data.filter(function (d, i) {
            if (d['SELLER'] == value) {
                return d;
            }
        })
        return filterdata
    }

    function onSelectChange() {
        var value = this.value;
        var fdata = filteredData(value);
        makeQtrCountBarChart(fdata, 'counts_by_seller')
    }

});