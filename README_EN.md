# w4

![vim](assets/vim_en.png)

Feature:

- Plain Text
- Reference(Track connections between events)
- set association
- Query expression
- Characters diagram
- Event diagram

## Settings

```
" set chrome path
let g:w4_chrome_path = ""

" set firefox path
let g:w4_firefox_path = ""
```

Enter the `:W4Go` command in vim to open the browsing window, press `enter` to open the input window, the effect is to imitate the appearance of the game chat window, the effect is as follows,

![home](assets/logic_en.png)

## w4 file format

The text starts with `%% who what when where` and looks like this:

```
%% col_split_char=/
%% who what when where
#0724073055 / @Ah Q / After drinking three bowls of wine, he boasted that he was in the same family as Mr. Zhao and was three generations older than his son / - / WeiZhuang
#0724073430 / @Mr. Zhao / Regarding Ah Q's forced relatives, he uttered the famous sentence: How could your surname be Zhao! Where do you deserve the surname Zhao / The next day / home / #0724073055
#0724073803 / @Ah Q / pimples on the head / - / -
#0724074006 / @Weichuang people / Make fun of Ah Q: Light up / - / - / #0724073803
```

They represent people, events, time, and places respectively, and the names start with @. It can be regarded as a 4-column database table, and the columns are separated by `/`. You can specify separator yourself in the file header. For example, you can add the following command to the file header to specify a slash (`/`) as the separator,

```
%% col_split_char=/
```

If the current column is empty, replace it with `-`. In actual use, I often find that the semantics of "same as above" and "same as above" are often expressed. "Same as above" uses `--`, and "same as above above" uses `---` . 

It can be seen that the sample text has more than four columns, because the first column is equivalent to id, which uniquely identifies a row, and the last column is an associated column, which is used to establish the connection between rows, see complete file in `/example/english.w4`.

## Autocomplete

- Enter the `@` symbol to automatically prompt all names
- Enter the `#` symbol to automatically prompt all rows
- Use `Tab` to trigger completion during the input process

![autocomplete](assets/autocmp_en.png)

## Query Expression

support:
- Special commands: start with `/`, there are currently three, `/home` displays all entries, `/characters` displays the character relationship diagram, `/events` displays the event relationship diagram.
- Logical expressions: and (&), or (|), not (!), equal to (=, fuzzy match), not equal to (!=)

For example, something related to Ah Q:

```
who=Ah Q
```

People or events include Little Nun:

```
who=little nun | what=little nun
```

What happened in WeiZhuang:

```
where=WeiZhuang
```

What happened in spring:

```
when=spring
```

## Characters diagram

input `/characters`

![who1](assets/who1_en.png)

## Events diagram

input `/events`

![backtrack](assets/backtrack1_en.png)





