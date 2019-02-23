### InPhO Corpus Builder
The InPhO Corpus Builder matches a plaintext bibliography to volumes in the HathiTrust.

## Prequisites

1.  Install [anystyle.io](http://anystyle.io) and Ruby dependencies by following the directions:
    
    ```
    sudo apt-get install ruby-dev
    gem install --user-install anystyle
    ```
    
    Note: you might need to add the `~/.gem/ruby/2.3.0/bin` dir to your `PATH`. The `gem install` will tell you.
    
2.  Install `rython` using distribute:

    ```
    pip install rython
    ```

## Usage

1.  Use `parse.py` to parse a file to the JSON format for the browser:

    ```
    python parse.py FILENAME
    ```

2.  Launch the Corpus Builder:

    ```
    python server.py -p 9024
    ```

3.  Open the Corpus Builder in a browser: [http://localhost:9024/](http://localhost:9024)

4.  When finished, use `extractids.py` to create a file with 1 HathiTrust ID per
    line for use with corpus download tools.

    ```
    python extractids.py www/out.json
    ```
