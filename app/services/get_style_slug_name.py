
def get_style_slugs_by_model(model_name):
    # Mapping of model names to their style slugs
    model_styles = {
        "bytedance": [
            "3d", "realistic_style", "angel", "anime_style", "japanese_comics",
            "princess_style", "dreamy", "ink_style", "new_monet_garden", "monets_garden",
            "exquisite_comic", "cyber_machinery", "chinese_style", "romantic", "ugly_clay",
            "cute_doll", "3d_gaming", "animated_movie", "doll"
        ],
        # You can keep adding more models like this:
        "custom-image-generation-v2": ["ghibli-anime,vintage-cartoon,simpsons,disney-animation,chibi-art,pixar-3d,funko-pop,yearbook-portrait,ukiyo-e,pop-art,impressionist,graffiti,tattoo-art,post-apocalyptic,steampunk,cyberpunk,synthwave,low-poly,voxel-art,claymation,papercraft"],
       
    }
    return model_styles.get(model_name.lower(), ["unknown-model"])
# # Example usage
# model = "custom-image-generation-v2"
# style_slugs = get_style_slugs_by_model(model)
# print(f"Style slugs for '{model}': {style_slugs}")
