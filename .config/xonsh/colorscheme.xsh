from xonsh.tools import register_custom_style

cafehaine = {
    "Token.Literal.String": "#DDAA00",
    "Token.Comment": "#00AA00",
    "Token.Operator": "#FF00FF",
    "Token.Operator.Word": "#FF00FF",
    "Token.Keyword": "#1199DD",
    "Token.Name.Builtin": "#22BBEE",
}

register_custom_style("cafehaine", cafehaine)
$XONSH_COLOR_STYLE="cafehaine"
