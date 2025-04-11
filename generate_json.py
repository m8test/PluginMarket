import json
import os
import re
import requests
from itertools import islice


def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def validate_url(url, label):
    if url:
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            if not response.ok:
                raise Exception(f"[{label}] Invalid URL: {url} - Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"[{label}] URL validation failed: {url} - {e}")


def check_readme_existence(repository_url, local_readme_path, label):
    def convert_github_url_to_raw_readme(url):
        """
        将 GitHub 仓库 URL 转为 raw 的 README.md 地址
        支持：
        - https://github.com/user/repo
        - https://github.com/user/repo/tree/branch
        """
        pattern_branch = r'https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)$'
        pattern_root = r'https://github\.com/([^/]+)/([^/]+)$'

        match = re.match(pattern_branch, url)
        if match:
            user, repo, branch = match.groups()
            return f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/README.md'

        match = re.match(pattern_root, url)
        if match:
            user, repo = match.groups()
            # 默认使用 main 分支
            return f'https://raw.githubusercontent.com/{user}/{repo}/main/README.md'

        # 不是 GitHub 仓库地址，则保留原方式
        return url.rstrip('/') + '/README.md'

    if repository_url:
        readme_url = convert_github_url_to_raw_readme(repository_url)
        try:
            response = requests.head(readme_url, allow_redirects=True, timeout=10)
            if response.ok:
                return readme_url
            else:
                print(f"[{label}] README.md not found at: {readme_url} - Status: {response.status_code}")
        except Exception as e:
            print(f"[{label}] repository README.md check failed: {readme_url} - {e}")

    if os.path.exists(local_readme_path):
        return "local"

    raise Exception(f"[{label}] Missing README.md (both remote and local)")


def process_directory(base_dir, subdir):
    latest_txt_path = os.path.join(base_dir, 'latest.txt')
    latest_content = read_file_content(latest_txt_path) if os.path.exists(latest_txt_path) else ""

    versions = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            download_url_path = os.path.join(item_path, 'download_url.txt')
            repository_path = os.path.join(item_path, 'repository.txt')
            local_readme_path = os.path.join(item_path, 'README.md')

            download_url = read_file_content(download_url_path) if os.path.exists(download_url_path) else ""
            repository = read_file_content(repository_path) if os.path.exists(repository_path) else ""

            validate_url(download_url, f"{subdir}/{item}/download_url")
            if repository:
                validate_url(repository, f"{subdir}/{item}/repository")

            _ = check_readme_existence(repository, local_readme_path, f"{subdir}/{item}/README.md")

            versions.append({
                "name": item,
                "download_url": download_url,
                "repository": repository
            })

    # ✅ 校验 latest 是否在 versions 中
    version_names = [v["name"] for v in versions]
    if latest_content and latest_content not in version_names:
        raise Exception(f"[{subdir}] latest.txt 的内容 '{latest_content}' 不在 versions 列表中: {version_names}")

    return {
        "latest": latest_content,
        "versions": versions
    }


def chunked_iterable(iterable, size):
    it = iter(iterable)
    for first in it:
        yield [first] + list(islice(it, size - 1))


def main():
    directories = ['common', 'builder', 'component', 'language', 'editor']
    items_per_page = 10

    for dir_name in directories:
        if os.path.exists(dir_name):
            subdirs = [item for item in os.listdir(dir_name) if os.path.isdir(os.path.join(dir_name, item))]
            subdirs.sort()

            output_folder = f'{dir_name}_output'
            os.makedirs(output_folder, exist_ok=True)

            for page_num, subdirs_chunk in enumerate(chunked_iterable(subdirs, items_per_page), start=1):
                page_data = []
                for subdir in subdirs_chunk:
                    subdir_path = os.path.join(dir_name, subdir)
                    data = process_directory(subdir_path, subdir)
                    data["name"] = subdir  # 👈 添加模块名字段
                    page_data.append(data)

                output_file = os.path.join(output_folder, f'page_{page_num}.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(page_data, f, indent=4, ensure_ascii=False)

                print(f"✅ Generated JSON for {dir_name}, page {page_num}: {output_file}")


if __name__ == "__main__":
    main()
