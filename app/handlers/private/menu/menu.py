from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from loguru import logger


from app.keyboard.inline.menu import back_to_menu_kb


router = Router()


@logger.catch()
@router.message(F.text == "ℹ️ Показать меню")
async def menu(msg: Message, state: FSMContext):
    """Button for calling main menu

    :param msg: message sent by the user
    :param state: inherit fsm
    :return: the output is several coroutines
    """
    logger.debug("main menu is called")
    # * cleaning all states just in case
    await state.clear()
    await msg.answer(
        "Мяу-мяу-мяу😻"
        "\n\n<b>Выберите нужное действие:</b>",
        reply_markup=main_menu()
    )

