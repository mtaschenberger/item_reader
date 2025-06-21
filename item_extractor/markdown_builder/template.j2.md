#item #{{ subcategory|capitalize }}
---
Category: "[[Items]]"
SubCategory: "[[{{ subcategory|capitalize }}]]"
Rarity: "[[{{ item.rarity|capitalize }}]]"
Requires Attunement: {{ "yes" if item.attunement else "no" }}
Cursed: {{ "yes" if item.curse else "no" }}
---

{%- if image_relpath %}
![[{{ image_relpath }}]] 

{%- endif %}

{{ item.description | trim }}

{%- if item.curse %}

#### Curse

{{ item.curse | trim }}
{%- endif %}