#!/bin/bash

# Define your layer types
LAYERS=(
  "Base"
  "Dots"
  "Line"
  "Gradient"
  "Brush Stroke"
  "Top Half"
)

# Define your colors
COLORS=(
  "Apple Crunch"
  "Aqua Lagoon"
  "Blue Pearl"
  "Caramelita"
  "Copper King"
  "Deep purple shimmer"
  "Fool Gold"
  "Forest Green"
  "Green Jade Pearl"
  "Gun Metal Grey"
  "Hello Yellow"
  "Lilac"
  "Lime shine"
  "Maroon Machine"
  "Midnight Blue"
  "Midnight Galaxy"
  "Mighty Mint"
  "Nancys Green Pearl"
  "Oh That Blue"
  "Pink"
  "Purple Rain"
  "Raa Ril Red"
  "Salmas Orange"
  "Sosase Silver"
)

# Create the folder structure
for layer in "${LAYERS[@]}"; do
  # Convert layer to lowercase_underscore
  layer_slug=$(echo "$layer" | tr '[:upper:]' '[:lower:]' | sed 's/ /_/g')

  for color in "${COLORS[@]}"; do
    # Convert color to lowercase_underscore
    color_slug=$(echo "$color" | tr '[:upper:]' '[:lower:]' | sed 's/ /_/g')

    # Create the folder, e.g. "chocolates/base/apple_crunch"
    mkdir -p "chocolates/${layer_slug}/${color_slug}"
    echo "Created folder: chocolates/${layer_slug}/${color_slug}"
  done
done

echo "All folders created!"