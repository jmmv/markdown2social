# Markdown2Social

**The Markdown2Social utility converts simple Markdown documents to Google+
posts ready to be shared on the social network.**  There is room for writing
output plugins for other target sites, but at the moment only Google+ is
supported.

This is not an official Google product.

## Why?

Long-form posts on social networks are more engaging than simply posting a bare
link to the exact same content hosted elsewhere.  However, composing long-form
posts on social networks is not a pleasant experience because their editors are
not designed to support long posts and because their formatting options are
severely limited.

What if you could write that same content in a more durable and flexible format,
say Markdown, and later export the text to the formats accepted by the networks
of your choice?  This would let you compose your posts using the myriad of
editors that support Markdown, would let you store those posts in a version
control system, and may even let you republish that same content directly on
your site with ease.

This is exactly the goal of Markdown2Social: to let you store your articles'
master copies in a version control system while providing a mechanism to extract
a simplified version that can be shared in a social network.  Does this work?
For the most part yes, but there are obvious limitations; keep reading.

## Download

The latest version of Markdown2Social is 0.2 and was released on
December 10th, 2015.

Download: [markdown2social-0.2](../../releases/tag/markdown2social-0.2)

See the [release notes](NEWS.md) for information about the changes in this and
all previous releases.

## Installation

Using `pip`:

```
$ pip install markdown2social
```

From sources after cloning the tree from GitHub:

```shell
$ ./setup.py install
```

See the [detailed installation instructions](INSTALL.md) for additional
information.

## Usage

1. Use `markdown2social` as a filter or with explicit file names to generate
   a `.gplus` file:

   ```shell
   $ markdown2social <doc.md >doc.gplus
   $ markdown2social -o doc.gplus doc.md
   ```

1. Open the `.gplus` file in your favorite editor.

1. Copy the whole contents to the clipboard.

1. Paste them into a new Google+ post.

1. Hit share and voil&agrave;!
