function setPrice(productId, count) {
    const metroPrice = parseFloat($('#price_metro_' + productId).text(), 10);
    const foziPrice = parseFloat($('#price_fozi_' + productId).text(), 10);
    const auchanPrice = parseFloat($('#price_auchan_' + productId).text(), 10);
    const novusPrice = parseFloat($('#price_novus_' + productId).text(), 10);

    const _calc = price => Math.round(price * 100 * count) / 100;

    if (metroPrice) {
        $('#price_metro_' + productId + '_sum').text(_calc(metroPrice));
    }
    if (foziPrice) {
        $('#price_fozi_' + productId + '_sum').text(_calc(foziPrice));
    }
    if (auchanPrice) {
        $('#price_auchan_' + productId + '_sum').text(_calc(auchanPrice));
    }
    if (novusPrice) {
        $('#price_novus_' + productId + '_sum').text(_calc(novusPrice));
    }
}


function set_total() {
    let metro_sum = 0, fozi_sum = 0, auchan_sum = 0, novus_sum = 0;
    const round = x => Math.round(x * 100) / 100;

    $('.metro_sum').each((i, el) => metro_sum += parseFloat(el.innerText || 0, 10));
    $('.fozi_sum').each((i, el) => fozi_sum += parseFloat(el.innerText || 0, 10));
    $('.auchan_sum').each((i, el) => auchan_sum += parseFloat(el.innerText || 0, 10));
    $('.novus_sum').each((i, el) => novus_sum += parseFloat(el.innerText || 0, 10));

    $('#metro_sum_total').text(round(metro_sum));
    $('#fozi_sum_total').text(round(fozi_sum));
    $('#auchan_sum_total').text(round(auchan_sum));
    $('#novus_sum_total').text(round(novus_sum));
}

$( document ).ready(function() {
    $('input.count').keyup(function(e) {
        const productId = $(e.target).data('product_id');
        const count = e.target.value;
        setPrice(productId, count);
        set_total();
    });
});