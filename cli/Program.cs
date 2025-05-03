using System;
using System.Collections.Generic;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.Diagnostics;
using System.IO;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.Dafny;
using static Microsoft.Dafny.DafnyMain;
using System.Linq;
using Std.Wrappers;

namespace DafnySketcherCli {
  class Program {
    static async Task<int> Main(string[] args) {
      // define options
      var fileOpt      = new System.CommandLine.Option<FileInfo>(new[]{ "--file", "-f" }, "Path to your .dfy");
      var sketchOpt    = new System.CommandLine.Option<string>(new[]{ "--sketch", "-s" }, "Sketch type") { IsRequired = true };
      var methodOpt    = new System.CommandLine.Option<string?>(new[]{ "--method", "-m" }, "Method name to target");
      var lineOpt      = new System.CommandLine.Option<int?>(new[]{ "--line", "-l" }, "Single line number to target");
      var rangeOpt     = new System.CommandLine.Option<string?>(new[]{ "--line-range", "-r" }, "Line range (start-end)");
      var replaceOpt   = new System.CommandLine.Option<bool>(new[]{ "--replace", "-x" }, "Apply sketch back into file");
      var promptOpt    = new System.CommandLine.Option<string?>(new[]{ "--prompt", "-p" }, "Optional sketch prompt");

      var root = new RootCommand("Dafny Sketcher CLI")
        { fileOpt, sketchOpt, methodOpt, lineOpt, rangeOpt, replaceOpt, promptOpt };

      root.SetHandler(async (InvocationContext context) => {
        // Retrieve parsed option values
        var file       = context.ParseResult.GetValueForOption(fileOpt);
        var sketchType = context.ParseResult.GetValueForOption(sketchOpt);
        var methodName = context.ParseResult.GetValueForOption(methodOpt);
        var line       = context.ParseResult.GetValueForOption(lineOpt);
        var range      = context.ParseResult.GetValueForOption(rangeOpt);
        var replace    = context.ParseResult.GetValueForOption(replaceOpt);
        var prompt     = context.ParseResult.GetValueForOption(promptOpt) ?? "";

        var filePath = file?.FullName;
        // Validate inputs
        if (filePath is not null && !File.Exists(filePath)) {
          await Console.Error.WriteLineAsync($"File not found: {filePath}");
          context.ExitCode = 1;
          return;
        }
        // TODO: Validate that only one of --method, --line, --line-range is set
        
        var options = DafnyOptions.Default;
        var reporter = new ConsoleErrorReporter(options);

        // Read the source text
        var source = "";
        Microsoft.Dafny.Program? dafnyProgram = null;
        if (filePath is not null) {
          await File.ReadAllTextAsync(filePath);

          // Parse & resolve using HandleDafnyFile and the new ParseCheck API
          // Load the file through the DafnyMain helper, so it respects search paths, includes, etc.
          var dafnyFile = DafnyFile.HandleDafnyFile(
            OnDiskFileSystem.Instance,
            reporter,
            options,
            new Uri(Path.GetFullPath(filePath)),
            Token.NoToken
          );
          var files = new List<DafnyFile> { dafnyFile };
          var (program, error) = await ParseCheck(
            TextReader.Null,
            files,
            "sketcher-cli",
            options
          );
          dafnyProgram = program;
        }

        // Figure out your target span
        var method = methodName is not null
          ? Utility.GetMethodByName(dafnyProgram, methodName)
          : null;
        int startLine = 0, endLine = 0;
        if (line.HasValue) {
          startLine = endLine = line.Value;
        } else if (!string.IsNullOrEmpty(range)) {
          var parts = range!.Split('-');
          startLine = int.Parse(parts[0]);
          endLine   = int.Parse(parts[1]);
        } else if (method != null) {
          startLine = method.Body.StartToken.line;
          endLine   = method.Body.EndToken.line - 1;
        }

        // 4) Instantiate the sketcher and fire it
        if (sketchType == "errors") { 
          // 2) Invoke `dafny verify` normally and capture its text output
          var psi = new ProcessStartInfo("dafny", $"verify \"{filePath}\"") {
            RedirectStandardOutput = true,
            RedirectStandardError  = true,
            UseShellExecute        = false,
          };
          using var proc = Process.Start(psi)!;
          var stdout = await proc.StandardOutput.ReadToEndAsync();
          var stderr = await proc.StandardError.ReadToEndAsync();
          proc.WaitForExit();
          var allText = stdout + "\n" + stderr;

          // 3) Pull out lines like: file.dfy(line,col): Error: message
          var diagnostics = new List<(int line, int col, string msg)>();
          // Match any line containing "(line,col):" followed by an optional "Error:" and the message
          var regex = new Regex(@"\((\d+),(\d+)\):\s*(?:Error:)?\s*(.*)");
          foreach (var rawLine in allText.Split('\n')) {
            //await Console.Error.WriteLineAsync($"DEBUG LINE: {rawLine}");
            if (!rawLine.Contains("Error:")) {
              continue;
            }
            var errLine = rawLine.Trim();
            var m    = regex.Match(errLine);
            if (m.Success) {
              //await Console.Error.WriteLineAsync($"DEBUG MATCH: {line}");
              diagnostics.Add((
                int.Parse(m.Groups[1].Value),
                int.Parse(m.Groups[2].Value),
                m.Groups[3].Value
              ));
            }
          }

          // Remove duplicate errors
          diagnostics = diagnostics.Distinct().ToList();

          // 4) Map each error pos into the enclosing Dafny method and print
          var lines = File.ReadAllLines(filePath).ToList();
          foreach (var (ln, col, msg) in diagnostics) {
            var m = Utility.GetEnclosingMethodByPosition(
              dafnyProgram, ln, col
            );
            var name = m?.Name ?? "<global>";
            var snippet = ln - 1 >= 0 && ln - 1 < lines.Count
              ? " -- in line: " + lines[ln - 1].Trim()
              : "";
            Console.WriteLine($"{name}:{ln}:{col} {msg}{snippet}");
          }

        } else {
          var sketcher = ISketcher.Create(sketchType, reporter);
          if (sketcher is null) {
            await Console.Error.WriteLineAsync("Error: sketcher unavailable for type " + sketchType);
            context.ExitCode = 1;
            return;
          }

          var req  = new SketchRequest(dafnyProgram, source, method, null, method?.StartToken.line, prompt);
          var resp = await sketcher.GenerateSketch(req);
          var sketch = resp.Sketch;
          var result = sketch;

          if (replace) {
            // 2) Read original lines
            var lines = File.ReadAllLines(filePath).ToList();

            // 3) Compute replace range
            int start = startLine, end = endLine;

            // 4) Replace those lines
            var sketchLines = sketch.Split('\n');
            lines.RemoveRange(start, end - start);
            lines.InsertRange(start, sketchLines);

            // 5) Output
            result = string.Join("\n", lines);
          }

          await Console.Out.WriteLineAsync(result);
        }
        context.ExitCode = 0;
        return;
      });
      return await root.InvokeAsync(args);
    }
  }
}