def create_shopping_cart_txt(ingredients):
    shopping_cart_txt = ''
    for ingredient in ingredients:
        shopping_cart_txt += (
            f'{ingredient["ingredient__name"]}, '
            f'{ingredient["ingredient__measurement_unit"]}, '
            f'{ingredient["final_sum"]} \n'
        )
    return shopping_cart_txt
