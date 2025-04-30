from jinja2 import Template

def generate_agent_description(profile):
    template_str = """
# About {{ agentName }}:
You are {{ agentName }}, an AI assistant specializing in Flutter development. Your primary goal is to engage in conversations and provide precise and pedagogical responses. Your personality and expertise are defined by the following attributes.

## 📝 Bio:
{% if bio %}{{ bio }}{% else %}Not provided{% endif %}

## 🔍 Background:
{% if lore %}{{ lore }}{% else %}Not provided{% endif %}

## 📚 Knowledge:
{% if knowledge %}{{ knowledge }}{% else %}Not provided{% endif %}

## ✍️ Communication Style:
{% if style %}{{ style }}{% else %}Not provided{% endif %}

## 🎭 Personality Traits:
{% if adjectives %}{{ adjectives }}{% else %}Not provided{% endif %}
"""
    
    template = Template(template_str)

    output = template.render(
        agentName=profile.get("name", "Agent"),
        language=profile.get("language", "Français"),
        bio="\n".join(profile.get("bio", ["Non renseigné"])),
        lore="\n".join(profile.get("lore", ["Non renseigné"])),
        knowledge=", ".join(profile.get("knowledge", ["Non renseigné"])),
        style=", ".join(profile.get("style", {}).get("all", ["Non renseigné"])),
        adjectives=", ".join(profile.get("adjectives", ["Non renseigné"]))
    )

    return output
