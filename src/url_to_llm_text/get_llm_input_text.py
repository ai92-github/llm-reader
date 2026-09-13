# SPDX-License-Identifier: MIT

from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from minify_html import minify
from inscriptis import get_text


async def get_processed_text(page_source: str, base_url: str,
                             html_parser: str ='lxml',
                             keep_images: bool =True, remove_svg_image: bool =True, remove_gif_image: bool =True, remove_image_types: list =[],
                             keep_webpage_links: bool =True,
                             remove_script_tag: bool =True, remove_style_tag: bool =True, remove_tags: list =[], extract: bool =False
                             ) -> str:
  """
  process html text. This helps the LLM to easily extract/scrape data especially image links, web links and tables.

  Args:
    page_source (str): html source text
    base_url (str): url of the html source.
    html_parser (str): which beautifulsoup html parser to use, defaults to 'lxml'
    keep_images (bool): keep image links. If False will remove image links from the text saving tokens to be processed by LLM. Default True
    remove_svg_image (bool): remove .svg image. usually not useful while scraping. default True
    remove_gif_image (bool): remove .gif image. usually not useful while scraping. default True
    remove_image_types (list): add any image extensions which you want to remove inside a list. eg: [.png]. Default []
    keep_webpage_links (bool): keep webpage links. if scraping job does not require links then can remove them to reduce input token count to LLM. Default True
    remove_script_tag (bool): True
    remove_style_tag (bool): True
    remove_tags (list): list of tags to be remove. Default []
    extract (bool): False. If using webpage text for data extarction then True.

  Returns (str):
    LLM ready input web page text
  """
  try:
    try:
      soup = BeautifulSoup(page_source, html_parser)
    except Exception as e:
      print('error in BeautifulSoup: ', str(e))
      soup = ''
    # -------remove tags----------
    remove_tag = []
    if remove_script_tag:
      remove_tag.append('script')
    if remove_style_tag:
      remove_tag.append('style')
    remove_tag.extend(remove_tags)
    remove_tag = list(set(remove_tag))
    for tag in soup.find_all(remove_tag):
      try:
        tag.extract()
      except Exception as e:
        print('Error while removing tag: ', e)
        continue

    # --------process image links--------
    remove_image_type = []
    if remove_svg_image:
      remove_image_type.append('.svg')
    if remove_gif_image:
      remove_image_type.append('.gif')
    remove_image_type.extend(remove_image_types)
    remove_image_type = list(set(remove_image_type))
    for image in (images := soup.find_all('img')):
      try:
        if not keep_images:
          image.replace_with('')
        else:
          image_link = image.get('src')
          type_replaced = False
          if type(image_link)==str:
            if remove_image_type!=[]:
              for image_type in remove_image_type:
                if not type_replaced and image_type in image_link:
                  image.replace_with('')
                  type_replaced=True
            if not type_replaced:
              image.replace_with('\n' + urljoin(base_url, image_link) + ' ')
      except Exception as e:
          print('Error while getting image link: ', e)
          continue

    # ----------process website links-----------
    for link in (urls := soup.find_all('a', href=True)):
      url_to_add = link['href']
      try:
        if not keep_webpage_links:
          link.replace_with('')
        else:
          link.replace_with(link.text + ': ' + urljoin(base_url, link['href']) + ' ')
      except Exception as e:
          print('Error while getting webpage link: ', e)
          continue

    # -----------process tables----------
    table_present = 0
    markdown=[]
    try:
      for tbs in (tables := soup.find_all('table')):
        try:
          try:
            caption_tag = tbs.find('caption')
            caption_text = caption_tag.get_text()
          except Exception as e:
            caption_text = ''
          header_row = tbs.find_all('tr')[0]
          headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
          if headers != []:
            markdown = ['| ' + ' | '.join(headers) + ' |']
            markdown.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
          current_row_header = None
          rowspan_count = 0
          for tr in tbs.find_all('tr')[1:]:
            cells = tr.find_all(['td', 'th'])
            if not cells:
              continue
            row_data = []

            # Check if first cell is a <th> with rowspan (row header)
            if cells[0].name == 'th' and cells[0].has_attr('rowspan'):
                current_row_header = cells[0].get_text(strip=True)
                rowspan_count = int(cells[0]['rowspan'])
                cells = cells[1:]  # Skip the row header cell
            elif cells[0].name == 'th':  # Regular row header (no rowspan)
                current_row_header = cells[0].get_text(strip=True)
                cells = cells[1:]

            # Only prepend a row header when the current row has one.
            if current_row_header is not None:
              row_data.append(current_row_header)

            # Append the rest of the data cells
            row_data.extend(cell.get_text(strip=True) for cell in cells)
            if row_data and ''.join(row_data)!='':
              markdown.append('| ' + ' | '.join(row_data) + ' |')
          if markdown != []:
            tbs.replace_with('ttaabbllee ssttaarrtt\n'+caption_text+'\n'+'\n'.join(markdown)+'\nttabbllee eenndd')
            table_present = table_present + 1
        except Exception as e:
          print('Error while getting individual table: ', e)
          try:
            header_row = tbs.find('tr')
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
            rows = []
            md_table = []
            for tr in tbs.find_all('tr')[1:]:
              row = []
              for cell in tr.find_all(['th', 'td']):
                  row.append(cell.get_text(strip=True))
              if ''.join(row)!=[]:
                rows.append(row)
            if headers!=[]:
              md_table.append('| ' + ' | '.join(headers) + ' |')
              md_table.append('|' + '---|' * len(headers))
            if rows!=[]:
              for row in rows:
                if ''.join(row)!=[]:
                  md_table.append('| ' + ' | '.join(row) + ' |')
            if md_table!=[]:
              markdown_result = '\n'.join(md_table)
              tbs.replace_with('ttaabbllee ssttaarrtt\n'+caption_text+'\n'+markdown_result+'\nttabbllee eenndd')
              table_present = table_present + 1
          except Exception as e:
            print('Error while getting indivdual tables 2nd time: ', e)
            continue
    except Exception as e:
      print('Error while getting taables: ', e)

    # -----------change text structure-----------
    if extract:
        text = soup.get_text()
    else:
        body_content = soup.find('body')
        if table_present == 0:
          if body_content:
              try:
                minimized_body = minify(str(body_content))
                text = get_text(minimized_body)
              except:
                text = get_text(str(body_content))
          else:
              text = soup.get_text()
        else:
          if body_content:
            text = ''
            body_content = str(body_content)
            start_idx = [ i.start() for i in re.finditer('ttaabbllee ssttaarrtt\n', body_content)]
            end_idx = [ i.end() for i in re.finditer('\nttabbllee eenndd', body_content)]
            if 1 not in start_idx:
                start_idx.insert(0,0)
            idxs = start_idx + end_idx
            idxs.sort()
            print('table break started')
            print(idxs)
            for i in range(len(idxs)):
              try:
                txt = body_content[idxs[i]:idxs[i+1]]
                if 'ttaabbllee ssttaarrtt\n' in txt:
                  txt = txt.replace('ttaabbllee ssttaarrtt\n','').replace('ttabbllee eenndd','')
                  text = text + '\n' + txt
                else:
                  txt = txt.replace('ttabbllee eenndd','')
                  try:
                    text = text + '\n' + get_text(minify(txt))
                  except:
                    text = text + '\n' + get_text(txt)
              except:
                txt = body_content[idxs[i]:]
                if 'ttaabbllee ssttaarrtt\n' in txt:
                  txt = txt.replace('ttaabbllee ssttaarrtt\n','').replace('ttabbllee eenndd','')
                  text = text + '\n' + txt
                else:
                  txt = txt.replace('ttabbllee eenndd','')
                  try:
                    text = text + '\n' + get_text(minify(txt))
                  except:
                    text = text + '\n' + get_text(txt)
          else:
              text = soup.get_text()
    return text

  except Exception as e:
    print('Error while getting processed text: ', e)
    return ''
