# Content Moderation

The following lists were updated to remove topics such as: nationalities, colours, body parts, emotions, religions, and social, political, health and legal terms.

- [LDNOOBW](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words) word list `./ldnoobw_words.txt`
- [Luis von Ahn's Research Group](https://www.cs.cmu.edu/~biglou/resources/) word list `./luis_von_ahn_bad_words.txt`

In cases where words are present from the aforementioned lists, the [OpenAI](https://platform.openai.com/docs/guides/moderation) content moderation endpoint is used to further check user input. 

To skip all moderation, set the following env var.

```bash
SKIP_MODERATION=true
```