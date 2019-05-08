
# feed parameters

```json
    "donedeal": {
        "name": "donedeal",
        'next_page_xpath': "//*[@id]",
        "next_button_text": "next",
        "result_stub": "https://www.donedeal.co.uk/cars-for-sale/",
        "wait_for": ".cad-header",
        "base_url": "https://donedeal.co.uk/cars",
        "result_stream": {
            "class": "card-item",
            "single": False
        },
    }
```

# mapping parameter

## results

    summary_feeds = {
        "donedeal": {
            "url": {
                "class": ['card__link'],  # the unique path in terms of classes to the tag containg the info
                "single": True,  # singleton data item or not. eg list of images == False
                "attr": "href", # the name of the attribute if a tag variable (eg. link) if text item let be none
                "name": "a", # the name of the tage to find

            },
            "price": {
                "class": ["card__price"],
                "single": True,
                "attr": None,
                "name": "span"
            },
            "imgs": {
                "class": ["card__photo"],
                "single": True,
                "attr": "src",
                "name": "img"
            },
            "attrs": {
                "class": ["card__body-keyinfo"],
                "single": False,
                "attr": None,
                "name": "li"
            }

        },

    }
