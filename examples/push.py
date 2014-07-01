from tamia import Repository

path = "path_to_repo"
repo = Repository(path)

content = "just some random content here"
with open("%s/new_file.txt" % path, "w+") as f:
  f.write(content)

repo.index.add("%s/new_file.txt" % path, content)
repo.index.commit("awesome message", "Author name", "Author email")
repo.push("origin", "master")
