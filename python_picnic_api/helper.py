import json
import re

# prefix components:
space = "    "
branch = "│   "
# pointers:
tee = "├── "
last = "└── "

IMAGE_SIZES = ["small", "medium", "regular", "large", "extra-large"]
IMAGE_BASE_URL = "https://storefront-prod.nl.picnicinternational.com/static/images"

def _tree_generator(response: list, prefix: str = ""):
    """A recursive tree generator,
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    # response each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(response) - 1) + [last]
    for pointer, item in zip(pointers, response):
        if "name" in item:  # print the item
            pre = ""
            if "unit_quantity" in item.keys():
                pre = f"{item['unit_quantity']} "
            after = ""
            if "display_price" in item.keys():
                after = f" €{int(item['display_price'])/100.0:.2f}"

            yield prefix + pointer + pre + item["name"] + after
        if "items" in item:  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from _tree_generator(item["items"], prefix=prefix + extension)


def _url_generator(url: str, country_code: str, api_version: str):
    return url.format(country_code.lower(), api_version)


def _get_category_id_from_link(category_link: str) -> str:
    pattern = r'categories/(\d+)'
    first_number = re.search(pattern, category_link)
    if first_number:
        result = str(first_number.group(1))
        return result
    else:
        return None


def _get_category_name(category_link: str, categories: list) -> str:
    category_id = _get_category_id_from_link(category_link)
    if category_id:
        category = next((item for item in categories if item["id"] == category_id), None)
        if category:
            return category["name"]
        else:
            return None
    else:
        return None

def get_recipe_image(id: str, size="regular"):
    sizes = IMAGE_SIZES + ["1250x1250"]
    assert size in sizes, "size must be one of: " + ", ".join(sizes)
    return f"{IMAGE_BASE_URL}/recipes/{id}/{size}.png"


def get_image(id: str, size="regular", suffix="webp"):
    assert "tile" in size if suffix == "webp" else True, (
        "webp format only supports tile sizes"
    )
    assert suffix in ["webp", "png"], "suffix must be webp or png"
    sizes = IMAGE_SIZES + [f"tile-{size}" for size in IMAGE_SIZES]

    assert size in sizes, (
        "size must be one of: " + ", ".join(sizes)
    )
    return f"{IMAGE_BASE_URL}/{id}/{size}.{suffix}"


def _extract_search_results(raw_results: dict) -> list:
    search_results = []
    sole_article_id_pattern = re.compile(r"sole_article_id=([0-9]+)")

    # Iterate over the nested structure of raw_results
    for child1 in raw_results.get("body", {}).get("children", []):
        for child2 in child1.get("children", []):
            content = child2.get("content")
            if content and "selling_unit" in content:
                # Extracting the sole_article_id from the serialized JSON of pml
                sole_article_ids = sole_article_id_pattern.findall(
                    json.dumps(child2.get("pml", {}))
                )
                if sole_article_ids:
                    sole_article_id = sole_article_ids[0]
                    # Create and append the result entry
                    result_entry = {
                        **content["selling_unit"],
                        "sole_article_id": sole_article_id,
                    }
                    search_results.append(result_entry)
    return search_results
