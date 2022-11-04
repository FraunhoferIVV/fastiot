import nest_asyncio

from fastiot_core_services.dash.dash_module import DashModule

if __name__ == '__main__':
    nest_asyncio.apply()
    DashModule.main()
