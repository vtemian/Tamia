from tamia import Repository


# if you want to use ssh protocol, libgit2 must be built with ssh support.
# https://github.com/libgit2/pygit2/issues/272
remote_url = "git://github.com/libgit2/pygit2.git"
repo = Repository.clone("repo", remote_url)

print repo.tags
