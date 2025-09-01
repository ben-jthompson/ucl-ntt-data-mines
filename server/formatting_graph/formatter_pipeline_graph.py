from ..session_state import SessionState
from .report_builder import ReportBuilder
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import json
import os
import zipfile
import shutil
from dotenv import load_dotenv
from ..utils import cancellable_node, should_cancel
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(model="gpt-4o-mini", temperature = 0, api_key=api_key)

@cancellable_node
def data_rewriter_node(state: SessionState) -> SessionState:
    """
    Rewrites the 'explanation', 'risk', and 'suitability' fields in each report section
    using the provided llm.
    """
    print("dwr node")
    report_sections = state.get("data_report_sections", [])
    with open('rep_sec.txt', 'w') as f:
        for sec in report_sections:
            f.write(str(sec))
    # with open("repo_sec.json", "r", encoding="utf-8") as f:
    #     report_sections = json.load(f)
    
    for idx, section in enumerate(report_sections):
        should_cancel(state)
        explanation = section['explanation']
        messages = [
            SystemMessage(content="You are a professional technical report writer, writing a feasibility report on different aspects affecting suitability of data centre placement within coal mines."),
            HumanMessage(
                content=(
                    "Rewrite the following text for clarity and conciseness, keeping the meaning exactly the same. Return only the rewritten text with no extra commentary:\n\n"
                    f"{explanation}"
                )
            )
        ]

        new_text = llm.invoke(messages)
        section['explanation'] = new_text.content
    state['data_report_sections'] = report_sections
    state['current'] = 'pdf_creation'
    return state

@cancellable_node
def pdf_creation_node(state: SessionState) -> SessionState:
    print("pdf")
    report_builder = ReportBuilder(client_id=state['client_id'], location=state['location'], data_report_sections=state['data_report_sections'], report_sections=state['report_sections'], bibliography=state['bibliography'])
    report_builder.run()
    metadata = report_builder.get_metadata()
    state["metadata"]["file_name"] = metadata['file_name']
    state["metadata"]["display_name"] = f'{state["location"]} Report {metadata["display_date"]}'
    state["metadata"]["upload_date"] = metadata['date'].isoformat()
    state["metadata"]["description"] = f'Report for location: {state["location"]}'
    state["metadata"]["coords"] = state["coords"]
    state['current'] = 'metadata'
    return state

@cancellable_node
def metadata_making_node(state: SessionState) -> SessionState:
    folder_path = os.path.join(os.getcwd(), "server/reports", state["client_id"], state['metadata']['file_name'][:-4])
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f'{state["metadata"]["file_name"]}.meta.json')
    with open(file_path, "w") as f:
        json.dump(state["metadata"], f, indent=2)
    state['current'] = 'zipper'
    return state

@cancellable_node
def zipper_node(state: SessionState) -> SessionState:
    upload_folder = os.path.join(os.getcwd(), "server/uploads", state['client_id'])
    report_folder = os.path.join(os.getcwd(), "server/reports", state['client_id'])
    os.makedirs(os.path.join(os.getcwd(), "server/reports", state['client_id'], state['metadata']['file_name'][:-4]), exist_ok=True)
    output_path = os.path.join(os.getcwd(), "server/reports", state['client_id'], state['metadata']['file_name'][:-4], f"Downloads_{state['metadata']['file_name'][:-4]}")
    report_output_path = os.path.join(os.getcwd(),"server/reports", state['client_id'], state['metadata']['file_name'][:-4], f"Report_{state['metadata']['file_name'][:-4]}.zip")
    
    if os.path.exists(upload_folder) and os.listdir(upload_folder):
        shutil.make_archive(output_path, "zip", upload_folder)
        shutil.rmtree(upload_folder)

    # with zipfile.ZipFile(report_output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    #     for file in [state['metadata']['file_name'], f"{state['metadata']['file_name']}.meta.json"]:
    #         abs_path = os.path.join(report_folder, file)
    #         if os.path.exists(abs_path):
    #             zipf.write(abs_path, file)

    state['current'] = 'done'
    return state

if __name__ == '__main__':
    metadata = pdf_creation_node({
    'location': 'Adderbury',
    'metadata': {},
    'coords': [53.1, -1.2],
    'client_id': '2ff3ade2-9405-47ee-8014-804361215db2',
    'bibliography': [{
        "file_name": "USER.pdf",
  "description": None,
  "tags": None,
  "id": "77d5deb8-d72b-4bd7-ad56-7e3a79108b34",
  "user": True
}, {
    "file_name": 'j2o.pdf',
  "description": None,
  "tags": None,
  "id": "77d5deb8-d72b-4bd7-ad56-7e3a79108b34",
  "link": "https://google.co.uk"
}],
    'report_sections': [
        {
            'topic': 'Farming',
            'suitability': 'High',
            'explanation': (
                "The soil in this area is fertile, well-drained, and ideal for crop rotation. Irrigation is readily available, and the climate supports a wide range of crops. Farmers can cultivate cereals, vegetables, and fruits throughout the year. "
                "Sustainable farming practices are encouraged to maintain soil quality and preserve "
                "biodiversity. The area also benefits from easy access to local markets and transportation "
                "routes, allowing farmers to sell produce efficiently. Additionally, there are several "
                "government programs and subsidies available for modern farming equipment, organic "
                "certifications, and water management systems. Crop rotation, composting, and natural pest "
                "management techniques ensure long-term productivity while protecting the environment. "
                "Community farming initiatives provide knowledge-sharing platforms that enhance crop yields "
                "and encourage environmentally-friendly farming practices across the region."
            )
        },
        {
            'topic': 'Urban Development',
            'suitability': 'Medium',
            'explanation': (
                "This area has moderate potential for urban development due to existing infrastructure, "
                "including road networks, electricity, and water supply. However, there are zoning "
                "regulations and land use restrictions that limit construction and expansion in certain zones. "
                "Development must consider environmental impact assessments and maintain a balance between "
                "green spaces and residential or commercial structures. The proximity to schools, hospitals, "
                "and shopping centers makes some neighborhoods attractive for new housing projects. "
                "Urban planning strategies should incorporate pedestrian-friendly pathways, public transportation, "
                "and community recreation spaces to improve the quality of life for residents. Developers are "
                "encouraged to adopt sustainable building techniques, such as energy-efficient materials, "
                "rainwater harvesting, and renewable energy sources. Collaboration with local authorities "
                "ensures compliance with municipal codes and promotes harmonious urban growth."
            )
        },
        {
            'topic': 'Conservation',
            'suitability': 'Low',
            'explanation': (
                "This region is primarily designated for conservation due to the presence of protected "
                "wildlife habitats and wetland ecosystems. Human activity is restricted to preserve the "
                "natural environment and biodiversity. The area is home to endangered species, native flora, "
                "and migratory birds that require careful monitoring. Conservation measures include controlled "
                "access for tourists, habitat restoration projects, and environmental education programs. "
                "Research initiatives focus on maintaining ecological balance and preventing habitat degradation. "
                "Local communities are engaged in sustainable practices, such as avoiding deforestation, "
                "minimizing pollution, and promoting eco-friendly livelihoods. This area offers limited "
                "opportunities for farming or urban development, but it plays a critical role in regional "
                "environmental health and climate resilience. Effective conservation strategies help maintain "
                "water quality, soil integrity, and carbon sequestration in the ecosystem."
            )
        },
        {
            'topic': 'Renewable Energy',
            'suitability': 'High',
            'explanation': (
                "The open fields and consistent wind patterns in this region make it highly suitable for "
                "renewable energy installations. Solar farms can take advantage of long hours of sunlight, "
                "while wind turbines can harness the frequent winds without obstruction from buildings or "
                "trees. Energy production from renewable sources provides economic opportunities and reduces "
                "dependence on fossil fuels. Local policies support investment in sustainable energy projects, "
                "including grants and tax incentives. Infrastructure for energy storage and grid integration is "
                "available, facilitating efficient distribution. Community awareness programs educate residents "
                "about the benefits of renewable energy, encouraging local support and participation. "
                "Environmental assessments ensure minimal impact on surrounding ecosystems, and technological "
                "advances continue to improve efficiency and reduce costs. Establishing renewable energy projects "
                "in this area contributes to long-term sustainability, energy security, and climate mitigation efforts."
            )
        },
        {
            'topic': 'Recreation',
            'suitability': 'Medium',
            'explanation': (
                "The scenic landscape and accessibility make this region suitable for recreational development. Parks, sports facilities, and walking trails can be designed to encourage outdoor activities and community engagement. Careful planning ensures that natural features such as lakes, forests, and hills are preserved while providing safe spaces for recreation. Facilities can include "
                "playgrounds, picnic areas, cycling paths, and outdoor fitness zones. Recreational development "
                "also promotes tourism and local business opportunities, such as cafes, rental shops, and guided "
                "tour services. Environmental sustainability is emphasized by using permeable surfaces, native "
                "plants, and waste management systems. Collaboration with local authorities and community groups "
                "ensures that recreation projects meet safety standards, accessibility requirements, and cultural "
                "needs. This balance between enjoyment and preservation makes the area a valuable resource for "
                "residents and visitors alike."
            )
        }
    ] * 4  # replicate to get 20 sections for testing
})
    metadata_making_node(metadata) 