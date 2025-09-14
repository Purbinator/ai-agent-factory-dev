# AI Agent Factory - Fejlesztési Környezet

Ez a repository a személyes AI Agent Factory fejlesztési környezetem, ahol különböző AI agent implementációkat és kísérleteket végzek.

## 🚀 Áttekintés

Ez a projekt az [Agent Factory with Subagents](./agent-factory/) koncepció alapján épül, és lehetőséget biztosít saját AI agent megoldások kifejlesztésére és tesztelésére.

## 📁 Projekt Struktúra

```
ai-agent-factory-dev/
├── agent-factory/          # Alapvető Agent Factory implementáció
│   ├── examples/           # Referencia implementációk
│   ├── CLAUDE.md          # Orchestration szabályok
│   └── README.md          # Agent Factory dokumentáció
├── projects/              # Saját projektek
├── experiments/           # Kísérleti implementációk
├── tools/                # Segédeszközök és utility-k
├── CLAUDE.md             # Fő orchestration fájl
└── README.md             # Ez a fájl
```

## 🛠️ Kezdés

### Előfeltételek

- Python 3.8+
- Git
- GitHub CLI (opcionális)
- Claude Desktop vagy MCP szerver kapcsolat

### Telepítés

1. Klónozd a repository-t:
```bash
git clone https://github.com/Purbinator/ai-agent-factory-dev.git
cd ai-agent-factory-dev
```

2. Tekintsd meg az alapvető Agent Factory dokumentációt:
```bash
cd agent-factory
cat README.md
```

## 📋 Használat

### Agent Factory Alapok

A projekt központi eleme a [CLAUDE.md](./CLAUDE.md) fájl, amely az orchestration szabályokat tartalmazza. Ez határozza meg, hogyan működnek együtt a különböző agent komponensek.

### Saját Projektek

A `projects/` könyvtárban hozhatsz létre saját AI agent projekteket:

```bash
mkdir projects/my-custom-agent
cd projects/my-custom-agent
# Itt fejlesztheted a saját agent implementációdat
```

### Kísérletek

Az `experiments/` könyvtár ad helyet próbálkozásoknak és prototípusoknak:

```bash
mkdir experiments/new-concept-test
# Teszteld új ötleteidet itt
```

## 🎯 Főbb Funkciók

- **Agent Factory Framework**: Komplett keretrendszer AI agent létrehozásához
- **Subagent Támogatás**: Specializált ágensek együttműködésének lehetősége  
- **RAG Integráció**: Retrieval Augmented Generation támogatás
- **MCP Kapcsolat**: Model Context Protocol integráció
- **GitHub Integration**: Közvetlen GitHub API használat

## 📖 Dokumentáció

- [Agent Factory Dokumentáció](./agent-factory/README.md)
- [CLAUDE Orchestration](./CLAUDE.md)
- [Példa Implementációk](./agent-factory/examples/)

## 🔧 Fejlesztői Környezet

### MCP Szerver Konfiguráció

A projekt GitHub MCP szervert használ. Győződj meg róla, hogy a `settings.json` megfelelően van konfigurálva:

```json
{
    "context_servers": {
        "mcp-server-github": {
            "source": "extension",
            "enabled": true,
            "settings": {
                "github_personal_access_token": "your_token_here"
            }
        }
    }
}
```

### Git Workflow

```bash
# Új feature branch készítése
git checkout -b feature/my-new-agent

# Változások commitálása
git add .
git commit -m "Add: új agent implementáció"

# Push a repository-ba
git push origin feature/my-new-agent
```

## 🚀 Következő Lépések

1. **Fedezd fel** az agent-factory példákat
2. **Hozz létre** saját agent projektet a `projects/` könyvtárban
3. **Kísérletezz** új koncepciókkal az `experiments/` területen
4. **Dokumentáld** a fejlesztéseidet
5. **Oszd meg** a hasznos implementációkat

## 📝 Changelog

- **2024-01-XX**: Initial setup - Agent Factory alapstruktúra létrehozva
- **2024-01-XX**: GitHub MCP integráció beállítva
- **2024-01-XX**: Projekt struktúra kialakítva

## 🤝 Közreműködés

Ez egy személyes fejlesztési környezet, de nyitott vagyok ötletekre és együttműködésre!

## 📄 Licenc

MIT License - lásd a [LICENSE](LICENSE) fájlt a részletekért.

---

**Happy Coding!** 🎉