SHORTCACHE_MAPPING = {
    'log_type': './td[1]/img[1]/attribute::title',
    'found_date': './td[3]/text()',
    'type': './td[4]//a[1]/img[1]/attribute::title',
    'title': './td[4]//a[2]//text()',
    'region': './td[5]//text()',
    'detail_link': './td[4]//a[1]/attribute::href'
}

GEOCACHE_MAPPING = {
    'geocode': '//*[@id="ctl00_ContentBody_CoordInfoLinkControl1_uxCoordInfoCode"]//text()',
    'title': '//*[@id="ctl00_ContentBody_CacheName"]//text()',
    'owner': '//*[@id="ctl00_ContentBody_mcd1"]/a//text()',
    'difficulty': '//*[@id="ctl00_ContentBody_uxLegendScale"]/img/attribute::src',
    'terrain': '//*[@id="ctl00_ContentBody_Localize12"]/img/attribute::src',
    'size': '//*[@id="ctl00_ContentBody_size"]/p/span/img/attribute::src',
    'coordinates': '//*[@id="uxLatLon"]//text()',
    'archived': 'boolean(//*[@id="divContentMain"]/div[3]/ul/li[contains(text(), \'This cache has been archived\')])'
}

SOUVENIR_ENTRY = '//*[@id="divContentMain"]/div[@class="ProfileSouvenirsList"]/div[starts-with(@id, "souvenir")]'
SHORT_SOUVENIR_MAPPING = {
    'title': 'a[1]/attribute::title',
    'image_url': 'a[1]/img[1]/attribute::src',
    'aquired_on': './text()[3]',
    'detail_link': 'a[1]/attribute::href'
}

SOUVENIR_MAPPING = {
    'title': '//*[@id="ctl00_ContentBody_SouvenirDisplayControl1_uxTitle"]//text()',
    'image': '//*[@id="ctl00_ContentBody_SouvenirDisplayControl1_uxLargeImage"]/attribute::src',
    'artist': '//*[@id="ctl00_ContentBody_SouvenirDisplayControl1_uxArtistNameWrapper"]/text()',
    'about_artist': '//*[@id="ctl00_ContentBody_SouvenirDisplayControl1_uxAboutTheArtist"]//text()',
    'additional_information': '//*[@id="ctl00_ContentBody_SouvenirDisplayControl1_uxInformation"]//text()'
}
