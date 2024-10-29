from dataclasses import dataclass


@dataclass
class Tag:
    """
    <attribute id="Description" type="LSString" value="test description"/>
    <attribute id="DisplayDescription" type="TranslatedString" handle="h6c83d504g5aa4g42abga0e7g770c9d830753"
               version="1"/>
    <attribute id="DisplayName" type="TranslatedString" handle="ha59594e8g8544g4bbdg82ddge6c19ba2bc6d"
               version="1"/>
    <attribute id="Icon" type="FixedString" value="icon"/>
    <attribute id="Name" type="FixedString" value="tag #1"/>
    <attribute id="UUID" type="guid" value="4b8dbf5b-68d8-4c1e-80c2-b68ce13a82c8"/>
    <children>
        <node id="Categories">
            <children>
                <node id="Category">
                    <attribute id="Name" type="LSString" value="Code"/>
                </node>
                <node id="Category">
                    <attribute id="Name" type="LSString" value="CharacterSheet"/>
                </node>
            </children>
        </node>
    </children>
    """

    name: str
    description: str
    display_description: str
    icon: str
    display_name: str
    uuid: str
    categories: list[str]
