from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


OUTPUT = Path(__file__).with_name("Anime_Shelf_presentation.pptx")

SLIDES = [
    {
        "title": "Anime Shelf",
        "subtitle": "Интернет-магазин аниме атрибутики на Django",
        "bullets": [
            "Семестровый проект по паттернам проектирования.",
            "Формат: локальное веб-приложение с БД, UI, аналитикой и демонстрацией паттернов.",
            "Цель: показать работающую систему и понимание примененных архитектурных решений.",
        ],
    },
    {
        "title": "Идея Проекта",
        "subtitle": "Что делает приложение",
        "bullets": [
            "Покупатель просматривает каталог, находит товар, кладет его в корзину и оформляет заказ.",
            "При оформлении система применяет стратегии цены и доставки.",
            "Менеджер получает заполненную БД, журнал событий процесса и аналитику спроса.",
        ],
    },
    {
        "title": "Этапы По ТЗ",
        "subtitle": "Что уже закрыто в проекте",
        "bullets": [
            "Этап 1: приложение, модели БД, BPMN, сущности и математическая модель.",
            "Этап 2: ERD, seed данных, Template Method, Strategy, Abstract Factory, Decorator.",
            "Этап 3: State, Adapter, Observer, Command и генерация элементов через шаблонный метод.",
            "Этап 4: пользовательский интерфейс, Proxy, Composite, Iterator и финальная диаграмма классов.",
            "Этап 5: подготовлены use case, рассказ и материалы для демонстрации.",
        ],
    },
    {
        "title": "Основные Бизнес-Процессы",
        "subtitle": "Отражены в BPMN",
        "bullets": [
            "Покупка товара: каталог -> корзина -> выбор стратегии -> checkout -> заказ -> события -> журнал.",
            "Наполнение каталога: seed-команда -> фабрики -> декораторы -> товары -> точки продаж -> прогноз.",
            "На диаграммах BPMN и Use Case показаны и пользовательские действия, и работа системы.",
        ],
    },
    {
        "title": "База Данных И Сущности",
        "subtitle": "Ключевые сущности системы",
        "bullets": [
            "Каталог: Category, Product, Review.",
            "Покупка: Customer, Cart, CartItem, Order, OrderItem.",
            "Аналитика и промо: Promotion, SalesPoint.",
            "Мониторинг процесса: ProcessLog.",
            "ERD показывает связи между каталогом, заказами, отзывами и точками продаж.",
        ],
    },
    {
        "title": "Математическая Модель",
        "subtitle": "Прогноз спроса по продажам",
        "bullets": [
            "Используется линейный тренд продаж y = ax + b.",
            "Входные данные: недельные точки SalesPoint для товара.",
            "Результат: направление спроса и прогноз продаж на следующую неделю.",
            "Модель применяется на главной странице и в карточке товара.",
        ],
    },
    {
        "title": "Паттерны Этапов 1-2",
        "subtitle": "Базовая бизнес-логика",
        "bullets": [
            "Strategy: расчет скидок и вариантов доставки.",
            "Singleton: настройки магазина, EventBus и реестры стратегий.",
            "Template Method: сценарий оформления заказа и генерация каталога.",
            "Abstract Factory: создание разных типов мерча.",
            "Decorator: добавление limited edition и gift wrap к данным товара.",
        ],
    },
    {
        "title": "Паттерны Этапов 3-4",
        "subtitle": "Интеграция, процессы и UI",
        "bullets": [
            "State: жизненный цикл заказа и допустимые переходы между статусами.",
            "Observer: журнал процесса, уведомления и контроль низкого остатка.",
            "Command: add to cart, update cart, checkout и смена статуса заказа.",
            "Adapter: подключение модуля трендов к рекомендациям магазина.",
            "Proxy: кэширование клиентского каталога.",
            "Composite и Iterator: дерево категорий и товаров для пользовательского представления.",
        ],
    },
    {
        "title": "Сценарии Использования",
        "subtitle": "Обновленный Use Case",
        "bullets": [
            "Покупатель: просмотреть каталог, найти товар, открыть карточку, добавить в корзину, выбрать скидку и доставку, оформить заказ, отслеживать статус.",
            "Менеджер: управлять каталогом, заполнять демо-БД, анализировать спрос, просматривать журнал процесса.",
            "Ключевой сценарий: оформление заказа включает выбор стратегий и порождает события процесса.",
        ],
    },
    {
        "title": "Маршрут Демонстрации",
        "subtitle": "Что показывать на защите",
        "bullets": [
            "Открыть главную страницу и поиск по каталогу.",
            "Показать карточку товара и блок прогноза спроса.",
            "Добавить товар в корзину, переключить скидку и доставку.",
            "Оформить заказ и поменять его состояния.",
            "Открыть страницы /patterns/ и /tree/ для сводной демонстрации паттернов.",
        ],
    },
    {
        "title": "Итог",
        "subtitle": "Что важно подчеркнуть в защите",
        "bullets": [
            "Проект соответствует ТЗ и охватывает паттерны из всех этапов.",
            "Система не только демонстрационная: паттерны встроены в реальные части приложения.",
            "Материалы защиты: диаграммы BPMN, ERD, state machine, class diagram, use case, рассказ и электронная доска.",
        ],
    },
]


def emu(value: int) -> str:
    return str(value)


def text_body_xml(paragraphs: list[str], level: int = 0, font_size: int = 2200) -> str:
    parts = []
    for index, paragraph in enumerate(paragraphs):
        bullet_attrs = f' lvl="{level}"' if level else ""
        bullet = "<a:buChar char=\"•\"/>" if index > -1 else ""
        parts.append(
            f"""
            <a:p>
              <a:pPr{bullet_attrs} marL="342900" indent="-171450">{bullet}</a:pPr>
              <a:r>
                <a:rPr lang="ru-RU" sz="{font_size}" dirty="0"/>
                <a:t>{escape(paragraph)}</a:t>
              </a:r>
              <a:endParaRPr lang="ru-RU" sz="{font_size}" dirty="0"/>
            </a:p>
            """
        )
    return "".join(parts)


def slide_xml(title: str, subtitle: str, bullets: list[str], slide_no: int) -> str:
    title_y = 457200
    subtitle_y = 1280160
    body_y = 1920240
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill><a:srgbClr val="F6F4EF"/></a:solidFill>
        <a:effectLst/>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="Title {slide_no}"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="685800" y="{emu(title_y)}"/>
            <a:ext cx="10972800" cy="685800"/>
          </a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="ru-RU" sz="3000" b="1"/>
              <a:t>{escape(title)}</a:t>
            </a:r>
            <a:endParaRPr lang="ru-RU" sz="3000"/>
          </a:p>
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="3" name="Subtitle {slide_no}"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="685800" y="{emu(subtitle_y)}"/>
            <a:ext cx="9144000" cy="457200"/>
          </a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="ru-RU" sz="1800" b="1">
                <a:solidFill><a:srgbClr val="D83A52"/></a:solidFill>
              </a:rPr>
              <a:t>{escape(subtitle)}</a:t>
            </a:r>
            <a:endParaRPr lang="ru-RU" sz="1800"/>
          </a:p>
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="4" name="Body {slide_no}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="914400" y="{emu(body_y)}"/>
            <a:ext cx="10363200" cy="4343400"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0">
            <a:spAutoFit/>
          </a:bodyPr>
          <a:lstStyle/>
          {text_body_xml(bullets)}
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="5" name="Footer {slide_no}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="914400" y="6400800"/>
            <a:ext cx="3200400" cy="228600"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="ru-RU" sz="1200">
                <a:solidFill><a:srgbClr val="666666"/></a:solidFill>
              </a:rPr>
              <a:t>Anime Shelf • Семестровый проект</a:t>
            </a:r>
            <a:endParaRPr lang="ru-RU" sz="1200"/>
          </a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>
"""


def content_types_xml(slide_count: int) -> str:
    overrides = "\n".join(
        f'  <Override PartName="/ppt/slides/slide{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for index in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
  <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
{overrides}
</Types>
"""


ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


APP_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office PowerPoint</Application>
  <PresentationFormat>On-screen Show (4:3)</PresentationFormat>
  <Slides>11</Slides>
  <Notes>0</Notes>
  <HiddenSlides>0</HiddenSlides>
  <MMClips>0</MMClips>
  <ScaleCrop>false</ScaleCrop>
  <HeadingPairs>
    <vt:vector size="2" baseType="variant">
      <vt:variant><vt:lpstr>Theme</vt:lpstr></vt:variant>
      <vt:variant><vt:i4>1</vt:i4></vt:variant>
    </vt:vector>
  </HeadingPairs>
  <TitlesOfParts>
    <vt:vector size="1" baseType="lpstr">
      <vt:lpstr>Office Theme</vt:lpstr>
    </vt:vector>
  </TitlesOfParts>
  <Company></Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>16.0000</AppVersion>
</Properties>
"""


def core_xml() -> str:
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Anime Shelf Presentation</dc:title>
  <dc:subject>Семестровый проект по паттернам проектирования</dc:subject>
  <dc:creator>Codex</dc:creator>
  <cp:keywords>Anime Shelf; patterns; Django; semester project</cp:keywords>
  <dc:description>Презентация проекта Anime Shelf по ТЗ семестровой работы.</dc:description>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>
</cp:coreProperties>
"""


def presentation_xml(slide_count: int) -> str:
    slide_ids = "\n".join(
        f'    <p:sldId id="{256 + index}" r:id="rId{index + 1}"/>'
        for index in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                saveSubsetFonts="1" autoCompressPictures="0">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId{slide_count + 1}"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
{slide_ids}
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen4x3"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle>
    <a:defPPr>
      <a:defRPr lang="ru-RU"/>
    </a:defPPr>
    <a:lvl1pPr marL="342900" indent="-171450">
      <a:defRPr sz="2200"/>
    </a:lvl1pPr>
  </p:defaultTextStyle>
</p:presentation>
"""


def presentation_rels_xml(slide_count: int) -> str:
    slide_rels = "\n".join(
        f'  <Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{index}.xml"/>'
        for index in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{slide_rels}
  <Relationship Id="rId{slide_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId{slide_count + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>
  <Relationship Id="rId{slide_count + 3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>
  <Relationship Id="rId{slide_count + 4}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
  <Relationship Id="rId{slide_count + 5}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>
</Relationships>
"""


SLIDE_MASTER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="Slide Master">
    <p:bg>
      <p:bgRef idx="1001">
        <a:schemeClr val="bg1"/>
      </p:bgRef>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rId1"/>
  </p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle>
      <a:lvl1pPr algn="l">
        <a:defRPr sz="3000" b="1"/>
      </a:lvl1pPr>
    </p:titleStyle>
    <p:bodyStyle>
      <a:lvl1pPr marL="342900" indent="-171450">
        <a:defRPr sz="2200"/>
      </a:lvl1pPr>
    </p:bodyStyle>
    <p:otherStyle>
      <a:defPPr/>
    </p:otherStyle>
  </p:txStyles>
</p:sldMaster>
"""


SLIDE_MASTER_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""


SLIDE_LAYOUT_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="titleOnly" preserve="1">
  <p:cSld name="Title Only">
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sldLayout>
"""


SLIDE_LAYOUT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""


PRES_PROPS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                  xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:showPr loop="0" useTimings="0"/>
</p:presentationPr>
"""


VIEW_PROPS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
          xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
          lastView="sldView">
  <p:normalViewPr horizBarState="restored" vertBarState="restored">
    <p:restoredLeft sz="15620"/>
    <p:restoredTop sz="94660"/>
  </p:normalViewPr>
  <p:slideViewPr>
    <p:cSldViewPr snapToGrid="1" snapToObjects="1" showGuides="1"/>
  </p:slideViewPr>
  <p:guideLst/>
</p:viewPr>
"""


TABLE_STYLES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>
"""


THEME_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
  <a:themeElements>
    <a:clrScheme name="Custom">
      <a:dk1><a:srgbClr val="17171F"/></a:dk1>
      <a:lt1><a:srgbClr val="F6F4EF"/></a:lt1>
      <a:dk2><a:srgbClr val="2F3340"/></a:dk2>
      <a:lt2><a:srgbClr val="FFFFFF"/></a:lt2>
      <a:accent1><a:srgbClr val="D83A52"/></a:accent1>
      <a:accent2><a:srgbClr val="F0A23B"/></a:accent2>
      <a:accent3><a:srgbClr val="3C7B7F"/></a:accent3>
      <a:accent4><a:srgbClr val="5884C4"/></a:accent4>
      <a:accent5><a:srgbClr val="8D5A97"/></a:accent5>
      <a:accent6><a:srgbClr val="748E54"/></a:accent6>
      <a:hlink><a:srgbClr val="0563C1"/></a:hlink>
      <a:folHlink><a:srgbClr val="954F72"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Simple Fonts">
      <a:majorFont>
        <a:latin typeface="Aptos Display"/>
        <a:ea typeface=""/>
        <a:cs typeface=""/>
      </a:majorFont>
      <a:minorFont>
        <a:latin typeface="Aptos"/>
        <a:ea typeface=""/>
        <a:cs typeface=""/>
      </a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Simple Format">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="lt1"/></a:solidFill>
        <a:solidFill><a:schemeClr val="accent1"/></a:solidFill>
        <a:solidFill><a:schemeClr val="accent2"/></a:solidFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="9525"><a:solidFill><a:schemeClr val="dk1"/></a:solidFill></a:ln>
        <a:ln w="25400"><a:solidFill><a:schemeClr val="accent1"/></a:solidFill></a:ln>
        <a:ln w="38100"><a:solidFill><a:schemeClr val="accent2"/></a:solidFill></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="lt1"/></a:solidFill>
        <a:solidFill><a:schemeClr val="lt2"/></a:solidFill>
        <a:solidFill><a:schemeClr val="dk1"/></a:solidFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
  <a:objectDefaults/>
  <a:extraClrSchemeLst/>
</a:theme>
"""


def slide_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>
"""


def build_pptx(output: Path) -> None:
    slide_count = len(SLIDES)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(slide_count))
        archive.writestr("_rels/.rels", ROOT_RELS)
        archive.writestr("docProps/app.xml", APP_XML)
        archive.writestr("docProps/core.xml", core_xml())

        archive.writestr("ppt/presentation.xml", presentation_xml(slide_count))
        archive.writestr("ppt/_rels/presentation.xml.rels", presentation_rels_xml(slide_count))
        archive.writestr("ppt/presProps.xml", PRES_PROPS_XML)
        archive.writestr("ppt/viewProps.xml", VIEW_PROPS_XML)
        archive.writestr("ppt/tableStyles.xml", TABLE_STYLES_XML)
        archive.writestr("ppt/theme/theme1.xml", THEME_XML)
        archive.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER_XML)
        archive.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS_XML)
        archive.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT_XML)
        archive.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS_XML)

        for index, slide in enumerate(SLIDES, start=1):
            archive.writestr(
                f"ppt/slides/slide{index}.xml",
                slide_xml(slide["title"], slide["subtitle"], slide["bullets"], index),
            )
            archive.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", slide_rels_xml())


if __name__ == "__main__":
    build_pptx(OUTPUT)
    print(OUTPUT)
