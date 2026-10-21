package io.github.serennity.ghosttrack;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.graphics.drawable.StateListDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.text.Editable;
import android.text.InputFilter;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.OutputStream;
import java.lang.ref.WeakReference;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;

/** Native, permission-minimal mobile client for the shared public-data services. */
public final class MainActivity extends Activity {
    private static final int BG = Color.rgb(8, 14, 23);
    private static final int PANEL = Color.rgb(16, 27, 42);
    private static final int INPUT = Color.rgb(23, 38, 56);
    private static final int LINE = Color.rgb(41, 65, 82);
    private static final int GREEN = Color.rgb(92, 240, 183);
    private static final int CYAN = Color.rgb(105, 217, 204);
    private static final int TEXT = Color.rgb(231, 244, 241);
    private static final int MUTED = Color.rgb(141, 169, 181);
    private static final int AMBER = Color.rgb(255, 199, 104);
    private static final int EXPORT_REQUEST = 300;
    private static final Handler MAIN = new Handler(Looper.getMainLooper());
    private final ThreadPoolExecutor workers = new ThreadPoolExecutor(2, 2, 10,
            TimeUnit.SECONDS, new ArrayBlockingQueue<>(2));
    private final List<AtomicBoolean> cancellationFlags = new ArrayList<>();
    private JSONObject config = new JSONObject(), ui = new JSONObject();
    private JSONArray tools = new JSONArray(), platforms = new JSONArray();
    private PyObject bridge;
    private String language = "zh", selectedTool = "域名综合报告";
    private String initialInput = "", initialPlatform = "", initialRegion = "CN";
    private String responseJson, resultToolTitle = "";
    private JSONObject result;
    private byte[] pendingExport;
    private long generation, startedAt;
    private boolean busy, building, destroyed, exporting;
    private AtomicBoolean currentCancel;
    private LinearLayout root, output, platformRow, regionRow;
    private EditText target, region, filter;
    private Spinner toolPicker, languagePicker, platformPicker;
    private Button runButton, cancelButton, copyButton, exportButton, exampleButton, pasteButton;
    private ProgressBar progress;
    private TextView status, fieldMetric, timeMetric, sourceLabel, hintLabel, resultCaption, contextTitle;

    private final Runnable ticker = new Runnable() {
        @Override public void run() {
            if (destroyed || !busy) return;
            if (timeMetric != null) timeMetric.setText(elapsed());
            MAIN.postDelayed(this, 200);
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        getWindow().getDecorView().setSystemUiVisibility(0);
        SharedPreferences prefs = getSharedPreferences("console", MODE_PRIVATE);
        language = prefs.getString("language", "zh");
        selectedTool = prefs.getString("tool", "域名综合报告");
        if (state != null) {
            language = state.getString("language", language);
            selectedTool = state.getString("tool", selectedTool);
            initialInput = state.getString("input", "");
            initialPlatform = state.getString("platform", "");
            initialRegion = state.getString("region", "CN");
            responseJson = state.getString("response");
            resultToolTitle = state.getString("result_title", "");
        }
        showBootScreen();
        bootstrap(language);
    }

    private void showBootScreen() {
        LinearLayout box = column();
        box.setPadding(dp(28), dp(36), dp(28), dp(36));
        box.setGravity(Gravity.CENTER);
        box.setBackgroundColor(BG);
        TextView brand = text("GHOSTTRACK", 28, GREEN, true);
        brand.setLetterSpacing(.12f);
        box.addView(brand);
        TextView subtitle = text("ANDROID / PUBLIC DATA CONSOLE", 10, MUTED, false);
        subtitle.setPadding(0, dp(16), 0, dp(24));
        box.addView(subtitle);
        ProgressBar bar = new ProgressBar(this);
        bar.setIndeterminateTintList(android.content.res.ColorStateList.valueOf(GREEN));
        box.addView(bar, new LinearLayout.LayoutParams(dp(32), dp(32)));
        setContentView(box);
        applyInsets(box);
    }

    private void bootstrap(String nextLanguage) {
        long token = ++generation;
        submit(new BootstrapTask(this, getApplicationContext(), nextLanguage, token));
    }

    private void acceptBootstrap(String json, PyObject module, String lang, long token) {
        if (token != generation) return;
        try {
            config = new JSONObject(json);
            ui = config.optJSONObject("ui");
            if (ui == null) ui = new JSONObject();
            tools = config.getJSONArray("tools");
            platforms = config.getJSONArray("platforms");
            bridge = module;
            language = lang;
            getSharedPreferences("console", MODE_PRIVATE).edit().putString("language", lang).apply();
            if (responseJson != null) {
                result = new JSONObject(responseJson).optJSONObject("result");
            }
            buildInterface();
        } catch (Exception error) {
            showBootError();
        }
    }

    private void showBootError() {
        LinearLayout box = column();
        box.setGravity(Gravity.CENTER);
        box.setPadding(dp(24), dp(24), dp(24), dp(24));
        box.setBackgroundColor(BG);
        box.addView(text("GHOSTTRACK", 24, GREEN, true));
        TextView message = text(local("服务初始化失败，请重试。", "Could not initialize services. Please retry.",
                "サービスの初期化に失敗しました。再試行してください。", "No se pudieron iniciar los servicios. Reinténtalo."), 16, TEXT, false);
        message.setPadding(0, dp(24), 0, dp(16));
        box.addView(message);
        Button retry = button(local("重试", "Retry", "再試行", "Reintentar"), true);
        retry.setOnClickListener(v -> { showBootScreen(); bootstrap(language); });
        box.addView(retry);
        setContentView(box);
        applyInsets(box);
    }

    private void buildInterface() {
        building = true;
        root = column();
        root.setBackgroundColor(BG);
        setContentView(root);
        applyInsets(root);

        LinearLayout appBar = row();
        appBar.setGravity(Gravity.CENTER_VERTICAL);
        appBar.setPadding(dp(16), dp(8), dp(12), dp(8));
        appBar.setBackgroundColor(PANEL);
        Radar emblem = new Radar(this);
        LinearLayout.LayoutParams emblemParams = new LinearLayout.LayoutParams(dp(38), dp(38));
        emblemParams.rightMargin = dp(9);
        appBar.addView(emblem, emblemParams);
        LinearLayout identity = column();
        TextView brand = text("GHOSTTRACK", 16, TEXT, true);
        brand.setLetterSpacing(.10f);
        identity.addView(brand);
        TextView edition = text("PUBLIC DATA / ANDROID", 8, CYAN, true);
        edition.setPadding(0, dp(5), 0, 0);
        edition.setLetterSpacing(.05f);
        identity.addView(edition);
        appBar.addView(identity, new LinearLayout.LayoutParams(0, -2, 1));
        languagePicker = spinner(languageNames());
        languagePicker.setContentDescription(t("language", "Language"));
        appBar.addView(languagePicker, new LinearLayout.LayoutParams(dp(106), dp(48)));
        Button help = button("?", false);
        help.setContentDescription(t("help", "Help"));
        help.setOnClickListener(v -> new AlertDialog.Builder(this).setTitle(t("help", "Help"))
                .setMessage(t("help_body", "Public sources only. Phone data does not identify account owners."))
                .setPositiveButton(t("close", "Close"), null).show());
        LinearLayout.LayoutParams helpParams = new LinearLayout.LayoutParams(dp(48), dp(48));
        helpParams.leftMargin = dp(6);
        appBar.addView(help, helpParams);
        root.addView(appBar);
        View divider = new View(this);
        divider.setBackgroundColor(LINE);
        root.addView(divider, new LinearLayout.LayoutParams(-1, dp(1)));

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setClipToPadding(false);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        LinearLayout content = column();
        content.setPadding(dp(16), dp(16), dp(16), dp(24));
        scroll.addView(content);

        contextTitle = text("", 24, TEXT, true);
        contextTitle.setPadding(0, 0, 0, dp(5));
        content.addView(contextTitle);
        TextView intro = text(local("公开来源 · 清晰溯源 · 复制与导出", "Public sources · Clear evidence · Copy & export",
                "公開情報 · 出典を確認 · コピーと保存", "Fuentes públicas · Datos claros · Copia y exporta"), 11, MUTED, false);
        intro.setLineSpacing(dp(2), 1);
        content.addView(intro);
        LinearLayout metrics = row();
        metrics.setPadding(0, dp(14), 0, dp(14));
        metric(metrics, Integer.toString(tools.length()), local("查询模块", "MODULES", "ツール", "MÓDULOS"));
        fieldMetric = metric(metrics, result == null ? "0" : Integer.toString(result.length()), local("结果字段", "FIELDS", "項目", "CAMPOS"));
        timeMetric = metric(metrics, "—", local("实际耗时", "ELAPSED", "経過時間", "TIEMPO"));
        content.addView(metrics);

        LinearLayout parameters = panel();
        content.addView(parameters);
        parameters.addView(kicker("01", t("parameters", "QUERY PARAMETERS")));
        toolPicker = spinner(labels(tools));
        toolPicker.setContentDescription(t("tools", "Tools"));
        parameters.addView(toolPicker, new LinearLayout.LayoutParams(-1, dp(52)));
        sourceLabel = text("", 10, CYAN, true);
        sourceLabel.setPadding(0, dp(9), 0, dp(2));
        parameters.addView(sourceLabel);
        hintLabel = text("", 12, MUTED, false);
        hintLabel.setLineSpacing(dp(2), 1);
        hintLabel.setPadding(0, dp(3), 0, dp(10));
        parameters.addView(hintLabel);

        platformRow = column();
        platformRow.addView(label(t("platform", "Platform")));
        platformPicker = spinner(labels(platforms));
        platformPicker.setContentDescription(t("platform", "Platform"));
        platformRow.addView(platformPicker, new LinearLayout.LayoutParams(-1, dp(52)));
        platformRow.setPadding(0, 0, 0, dp(10));
        parameters.addView(platformRow);

        regionRow = column();
        regionRow.addView(label(t("region_label", "Phone region (ISO, e.g. CN)")));
        region = input("CN");
        region.setSingleLine(true);
        region.setFilters(new InputFilter[]{new InputFilter.LengthFilter(2), new InputFilter.AllCaps()});
        region.setText(initialRegion);
        region.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS);
        regionRow.addView(region, new LinearLayout.LayoutParams(-1, dp(52)));
        regionRow.setPadding(0, 0, 0, dp(10));
        parameters.addView(regionRow);

        target = input(t("input", "Target"));
        target.setMinLines(1);
        target.setMaxLines(4);
        target.setGravity(Gravity.TOP | Gravity.START);
        target.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE
                | android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        target.setFilters(new InputFilter[]{new InputFilter.LengthFilter(4096)});
        target.setImeOptions(EditorInfo.IME_ACTION_DONE);
        target.setText(initialInput);
        target.setContentDescription(t("input", "Target"));
        target.setMinHeight(dp(60));
        parameters.addView(target, new LinearLayout.LayoutParams(-1, -2));
        LinearLayout inputActions = row();
        inputActions.setPadding(0, dp(6), 0, dp(6));
        exampleButton = button(t("example", "Example"), false);
        pasteButton = button(t("paste", "Paste"), false);
        weightedButton(inputActions, exampleButton, true);
        weightedButton(inputActions, pasteButton, false);
        parameters.addView(inputActions);
        exampleButton.setOnClickListener(v -> {
            target.setText(toolAt(toolPicker.getSelectedItemPosition()).optString("example"));
            target.setSelection(target.length());
        });
        pasteButton.setOnClickListener(v -> pasteInput());
        LinearLayout queryActions = row();
        runButton = button(t("run", "Run query"), true);
        cancelButton = button(t("cancel", "Cancel"), false);
        weightedButton(queryActions, runButton, true);
        weightedButton(queryActions, cancelButton, false);
        cancelButton.setEnabled(false);
        parameters.addView(queryActions);
        runButton.setOnClickListener(v -> runQuery());
        cancelButton.setOnClickListener(v -> cancelQuery());
        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progress.setIndeterminate(true);
        progress.setIndeterminateTintList(android.content.res.ColorStateList.valueOf(GREEN));
        progress.setVisibility(View.GONE);
        LinearLayout.LayoutParams progressParams = new LinearLayout.LayoutParams(-1, dp(3));
        progressParams.topMargin = dp(14);
        parameters.addView(progress, progressParams);
        status = text(t("ready", "Ready"), 12, MUTED, false);
        status.setPadding(0, dp(10), 0, 0);
        status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        parameters.addView(status);

        LinearLayout resultsPanel = panel();
        LinearLayout.LayoutParams resultParams = new LinearLayout.LayoutParams(-1, -2);
        resultParams.topMargin = dp(14);
        content.addView(resultsPanel, resultParams);
        resultsPanel.addView(kicker("02", t("results", "RESULTS")));
        resultCaption = text(resultToolTitle, 12, MUTED, false);
        resultCaption.setPadding(0, 0, 0, dp(10));
        resultsPanel.addView(resultCaption);
        filter = input(t("filter", "Filter fields or values"));
        filter.setSingleLine(true);
        filter.setFilters(new InputFilter[]{new InputFilter.LengthFilter(160)});
        filter.setContentDescription(t("filter", "Filter fields or values"));
        resultsPanel.addView(filter, new LinearLayout.LayoutParams(-1, dp(52)));
        LinearLayout exportActions = row();
        exportActions.setPadding(0, dp(10), 0, dp(8));
        copyButton = button(t("copy", "Copy all"), false);
        exportButton = button(t("export", "Export"), false);
        weightedButton(exportActions, copyButton, true);
        weightedButton(exportActions, exportButton, false);
        copyButton.setOnClickListener(v -> copyAll());
        exportButton.setOnClickListener(v -> chooseExport());
        resultsPanel.addView(exportActions);
        output = column();
        resultsPanel.addView(output);
        filter.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) { }
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) { renderResults(); }
            @Override public void afterTextChanged(Editable e) { }
        });

        TextView footer = text("GHOSTTRACK / " + t("privacy", "Public data · Respect privacy") + "\n" + t("notice", "Locations are estimates, never live tracking."), 11, MUTED, false);
        footer.setLineSpacing(dp(4), 1);
        footer.setPadding(dp(4), dp(20), dp(4), 0);
        content.addView(footer);

        int languageIndex = 0;
        JSONArray languages = config.optJSONArray("languages");
        for (int i = 0; languages != null && i < languages.length(); i++) {
            if (language.equals(languages.optJSONObject(i).optString("code"))) languageIndex = i;
        }
        languagePicker.setSelection(languageIndex, false);
        int toolIndex = 0;
        for (int i = 0; i < tools.length(); i++) {
            if (selectedTool.equals(toolAt(i).optString("id"))) toolIndex = i;
        }
        toolPicker.setSelection(toolIndex, false);
        for (int i = 0; i < platforms.length(); i++) {
            if (initialPlatform.equals(platforms.optJSONObject(i).optString("id"))) platformPicker.setSelection(i, false);
        }
        updateTool(false);
        toolPicker.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                String next = toolAt(position).optString("id");
                if (!building && !next.equals(selectedTool)) updateTool(true);
            }
            @Override public void onNothingSelected(AdapterView<?> parent) { }
        });
        languagePicker.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                JSONArray choices = config.optJSONArray("languages");
                if (building || choices == null) return;
                String next = choices.optJSONObject(position).optString("code", "zh");
                if (next.equals(language)) return;
                captureInputs();
                result = null;
                responseJson = null;
                resultToolTitle = "";
                showBootScreen();
                bootstrap(next);
            }
            @Override public void onNothingSelected(AdapterView<?> parent) { }
        });
        building = false;
        renderResults();
    }

    private void updateTool(boolean changed) {
        JSONObject tool = toolAt(toolPicker.getSelectedItemPosition());
        selectedTool = tool.optString("id");
        contextTitle.setText(tool.optString("title"));
        sourceLabel.setText("↗ " + tool.optString("source"));
        hintLabel.setText(tool.optString("hint"));
        boolean self = selectedTool.equals("本机公网 IP");
        platformRow.setVisibility(selectedTool.equals("国内平台") ? View.VISIBLE : View.GONE);
        regionRow.setVisibility(selectedTool.equals("号码归属地") ? View.VISIBLE : View.GONE);
        target.setEnabled(!self);
        exampleButton.setEnabled(!self);
        pasteButton.setEnabled(!self);
        if (changed) {
            target.setText("");
            clearResults();
            status.setText(t("ready", "Ready"));
        }
        getSharedPreferences("console", MODE_PRIVATE).edit().putString("tool", selectedTool).apply();
    }

    private void runQuery() {
        if (busy || bridge == null) return;
        String value = target.getText().toString().trim();
        if (value.isEmpty() && !selectedTool.equals("本机公网 IP")) {
            target.setError(t("empty_input", "Enter a query value"));
            target.requestFocus();
            return;
        }
        String regionCode = region.getText().toString().trim().toUpperCase(Locale.ROOT);
        if (regionCode.isEmpty()) regionCode = "CN";
        if (selectedTool.equals("号码归属地") && !regionCode.matches("[A-Z]{2}")) {
            region.setError(t("region_label", "Use a two-letter region, e.g. CN"));
            return;
        }
        String platform = platforms.optJSONObject(platformPicker.getSelectedItemPosition()).optString("id", "Bilibili");
        clearResults();
        currentCancel = new AtomicBoolean(false);
        synchronized (cancellationFlags) { cancellationFlags.add(currentCancel); }
        long token = ++generation;
        startedAt = SystemClock.elapsedRealtime();
        setBusy(true);
        status.setText(t("busy", "Querying…"));
        resultToolTitle = toolAt(toolPicker.getSelectedItemPosition()).optString("title");
        resultCaption.setText(resultToolTitle);
        InputMethodManager keyboard = (InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
        if (keyboard != null) keyboard.hideSoftInputFromWindow(target.getWindowToken(), 0);
        if (!submit(new QueryTask(this, bridge, token, currentCancel, selectedTool, value, regionCode, language, platform))) {
            currentCancel.set(true);
            setBusy(false);
            status.setText(t("thread_wait", "Previous requests are finishing; please retry shortly"));
        }
    }

    private void acceptQuery(String json, long token, AtomicBoolean cancel) {
        synchronized (cancellationFlags) { cancellationFlags.remove(cancel); }
        if (token != generation || cancel.get()) return;
        setBusy(false);
        timeMetric.setText(elapsed());
        try {
            JSONObject response = new JSONObject(json);
            if (response.optBoolean("cancelled")) {
                status.setText(t("cancelled", "Cancelled"));
                return;
            }
            if (!response.optBoolean("ok")) {
                JSONObject error = response.optJSONObject("error");
                status.setText(t("failed", "Query failed") + " · " + (error == null ? t("network_error", "Please retry") : error.optString("message", t("network_error", "Please retry"))));
                status.setTextColor(AMBER);
                return;
            }
            result = response.getJSONObject("result");
            responseJson = json;
            fieldMetric.setText(Integer.toString(result.length()));
            String stamp = new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date());
            resultCaption.setText(resultToolTitle + " / " + stamp);
            JSONObject raw = response.optJSONObject("raw");
            String pageStatus = raw == null ? "" : raw.optString("页面状态");
            boolean limited = raw != null && (raw.optString("查询状态").equals("部分来源不可用")
                    || (!pageStatus.isEmpty() && !pageStatus.startsWith("已读取页面元信息")));
            status.setText(limited ? t("limited", "Some sources are limited; review individual statuses") : t("done", "Query complete"));
            status.setTextColor(limited ? AMBER : GREEN);
            renderResults();
        } catch (JSONException error) {
            status.setText(t("failed", "Query failed") + " · " + t("network_error", "Please retry"));
            status.setTextColor(AMBER);
        }
    }

    private void cancelQuery() {
        if (!busy) return;
        if (currentCancel != null) currentCancel.set(true);
        ++generation;
        setBusy(false);
        timeMetric.setText(elapsed());
        status.setText(t("cancelled", "Cancelled"));
        status.setTextColor(MUTED);
    }

    private void setBusy(boolean value) {
        busy = value;
        runButton.setEnabled(!value);
        cancelButton.setEnabled(value);
        toolPicker.setEnabled(!value);
        languagePicker.setEnabled(!value);
        platformPicker.setEnabled(!value);
        region.setEnabled(!value);
        target.setEnabled(!value && !selectedTool.equals("本机公网 IP"));
        exampleButton.setEnabled(!value && !selectedTool.equals("本机公网 IP"));
        pasteButton.setEnabled(!value && !selectedTool.equals("本机公网 IP"));
        progress.setVisibility(value ? View.VISIBLE : View.GONE);
        status.setTextColor(MUTED);
        MAIN.removeCallbacks(ticker);
        if (value) MAIN.post(ticker);
    }

    private void clearResults() {
        result = null;
        responseJson = null;
        resultToolTitle = "";
        fieldMetric.setText("0");
        timeMetric.setText("—");
        resultCaption.setText("");
        filter.setText("");
        renderResults();
    }

    private void renderResults() {
        if (output == null) return;
        output.removeAllViews();
        boolean hasResult = result != null && result.length() > 0;
        copyButton.setEnabled(hasResult);
        exportButton.setEnabled(hasResult && !exporting);
        filter.setEnabled(hasResult);
        if (!hasResult) {
            LinearLayout empty = row();
            empty.setPadding(0, dp(12), 0, dp(10));
            empty.setGravity(Gravity.CENTER_VERTICAL);
            LinearLayout.LayoutParams radarParams = new LinearLayout.LayoutParams(dp(56), dp(56));
            radarParams.rightMargin = dp(12);
            empty.addView(new Radar(this), radarParams);
            LinearLayout description = column();
            TextView message = text(t("empty", "Your next discovery starts here"), 15, TEXT, true);
            message.setPadding(0, 0, 0, dp(7));
            description.addView(message);
            TextView help = text(local("选择模块、填写目标，开始查询。", "Choose a module and target to begin.",
                    "ツールと対象を選んで検索を開始。", "Elige un módulo y objetivo para empezar."), 12, MUTED, false);
            help.setLineSpacing(dp(3), 1);
            description.addView(help);
            empty.addView(description, new LinearLayout.LayoutParams(0, -2, 1));
            output.addView(empty);
            return;
        }
        String needle = filter.getText().toString().toLowerCase(Locale.ROOT);
        int shown = 0;
        Iterator<String> keys = result.keys();
        while (keys.hasNext()) {
            String key = keys.next();
            Object raw = result.opt(key);
            String value = raw == null || raw == JSONObject.NULL ? "—" : raw.toString();
            if (!needle.isEmpty() && !(key + "\n" + value).toLowerCase(Locale.ROOT).contains(needle)) continue;
            shown++;
            LinearLayout card = column();
            card.setPadding(dp(14), dp(6), dp(14), dp(15));
            card.setBackground(round(INPUT, LINE, 12));
            LinearLayout.LayoutParams cp = new LinearLayout.LayoutParams(-1, -2);
            cp.topMargin = dp(8);
            output.addView(card, cp);
            LinearLayout heading = row();
            heading.setGravity(Gravity.CENTER_VERTICAL);
            TextView field = text(key, 12, CYAN, true);
            heading.addView(field, new LinearLayout.LayoutParams(0, -2, 1));
            Button copy = button(local("复制", "Copy", "コピー", "Copiar"), false);
            copy.setTextSize(11);
            copy.setContentDescription(t("copy_selected", "Copy value") + ": " + key);
            copy.setOnClickListener(v -> copyText(value));
            heading.addView(copy, new LinearLayout.LayoutParams(-2, dp(48)));
            card.addView(heading);
            TextView detail = text(value, 14, TEXT, false);
            detail.setTypeface(Typeface.MONOSPACE);
            detail.setTextIsSelectable(true);
            detail.setLineSpacing(dp(4), 1);
            card.addView(detail, new LinearLayout.LayoutParams(-1, -2));
        }
        if (shown == 0) {
            TextView none = text(local("没有匹配的字段", "No matching fields", "一致する項目はありません", "No hay campos coincidentes"), 14, MUTED, false);
            none.setPadding(0, dp(20), 0, dp(20));
            output.addView(none);
        }
    }

    private void pasteInput() {
        ClipboardManager clipboard = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
        if (clipboard == null || !clipboard.hasPrimaryClip() || clipboard.getPrimaryClip() == null) {
            toast(t("clipboard_empty", "No text in the clipboard"));
            return;
        }
        CharSequence value = clipboard.getPrimaryClip().getItemAt(0).coerceToText(this);
        if (value == null) { toast(t("clipboard_empty", "No text in the clipboard")); return; }
        target.setText(value.toString().substring(0, Math.min(value.length(), 4096)));
        target.setSelection(target.length());
    }

    private void copyText(String value) {
        ClipboardManager clipboard = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
        if (clipboard != null) {
            clipboard.setPrimaryClip(ClipData.newPlainText("GhostTrack", value));
            toast(t("copied", "Copied"));
        }
    }

    private void copyAll() {
        if (result == null) return;
        StringBuilder report = new StringBuilder();
        Iterator<String> keys = result.keys();
        while (keys.hasNext()) {
            String key = keys.next();
            report.append(key).append(": ").append(result.optString(key, "—")).append('\n');
        }
        copyText(report.toString().trim());
    }

    private void chooseExport() {
        if (result == null || responseJson == null || exporting) return;
        String[] formats = {"JSON", "CSV", "HTML"};
        new AlertDialog.Builder(this).setTitle(t("export_type", "Report format"))
                .setItems(formats, (dialog, which) -> {
                    exporting = true;
                    exportButton.setEnabled(false);
                    String format = formats[which].toLowerCase(Locale.ROOT);
                    if (!submit(new ReportTask(this, bridge, responseJson, format))) {
                        exporting = false;
                        exportButton.setEnabled(result != null);
                    }
                }).setNegativeButton(t("cancel", "Cancel"), null).show();
    }

    private void acceptReport(String report, String format) {
        exporting = false;
        if (exportButton != null) exportButton.setEnabled(result != null);
        if (report == null) { toast(t("export_failed", "Export failed")); return; }
        pendingExport = report.getBytes(StandardCharsets.UTF_8);
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType(format.equals("json") ? "application/json" : format.equals("csv") ? "text/csv" : "text/html");
        intent.putExtra(Intent.EXTRA_TITLE, "GhostTrack-" + new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.ROOT).format(new Date()) + "." + format);
        try {
            startActivityForResult(intent, EXPORT_REQUEST);
        } catch (RuntimeException error) {
            pendingExport = null;
            toast(t("export_failed", "Export failed"));
        }
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != EXPORT_REQUEST) return;
        byte[] bytes = pendingExport;
        pendingExport = null;
        if (resultCode != RESULT_OK || data == null || data.getData() == null) return;
        if (bytes == null) {
            toast(local("导出已中断，请重新导出。", "Export was interrupted. Please export again.", "保存が中断されました。再実行してください。", "La exportación se interrumpió. Vuelve a exportar."));
            return;
        }
        submit(new SaveTask(this, getApplicationContext().getContentResolver(), data.getData(), bytes));
    }

    private void captureInputs() {
        if (target != null) initialInput = target.getText().toString();
        if (region != null) initialRegion = region.getText().toString();
        if (platformPicker != null && platforms.length() > 0) {
            initialPlatform = platforms.optJSONObject(platformPicker.getSelectedItemPosition()).optString("id");
        }
    }

    @Override protected void onSaveInstanceState(Bundle out) {
        captureInputs();
        out.putString("language", language);
        out.putString("tool", selectedTool);
        out.putString("input", initialInput);
        out.putString("platform", initialPlatform);
        out.putString("region", initialRegion);
        if (responseJson != null && responseJson.length() < 200000) out.putString("response", responseJson);
        out.putString("result_title", resultToolTitle);
        super.onSaveInstanceState(out);
    }

    @Override protected void onDestroy() {
        destroyed = true;
        ++generation;
        synchronized (cancellationFlags) { for (AtomicBoolean flag : cancellationFlags) flag.set(true); }
        MAIN.removeCallbacks(ticker);
        workers.shutdownNow();
        super.onDestroy();
    }

    private boolean submit(Runnable task) {
        try { workers.execute(task); return true; }
        catch (RejectedExecutionException error) {
            if (!destroyed && status != null) toast(t("thread_wait", "Previous requests are finishing; retry shortly"));
            return false;
        }
    }

    private static void deliver(WeakReference<MainActivity> reference, Consumer<MainActivity> action) {
        MAIN.post(() -> {
            MainActivity activity = reference.get();
            if (activity != null && !activity.destroyed && !activity.isFinishing()) action.accept(activity);
        });
    }

    private static final class BootstrapTask implements Runnable {
        final WeakReference<MainActivity> activity;
        final Context context;
        final String language;
        final long token;
        BootstrapTask(MainActivity activity, Context context, String language, long token) {
            this.activity = new WeakReference<>(activity); this.context = context; this.language = language; this.token = token;
        }
        @Override public void run() {
            try {
                synchronized (Python.class) {
                    if (!Python.isStarted()) Python.start(new AndroidPlatform(context));
                }
                PyObject module = Python.getInstance().getModule("mobile_bridge");
                String json = module.callAttr("bootstrap", language).toString();
                deliver(activity, a -> a.acceptBootstrap(json, module, language, token));
            } catch (Exception error) { deliver(activity, MainActivity::showBootError); }
        }
    }

    private static final class QueryTask implements Runnable {
        final WeakReference<MainActivity> activity;
        final PyObject bridge;
        final long token;
        final AtomicBoolean cancel;
        final String kind, value, region, language, platform;
        QueryTask(MainActivity activity, PyObject bridge, long token, AtomicBoolean cancel, String kind, String value, String region, String language, String platform) {
            this.activity = new WeakReference<>(activity); this.bridge = bridge; this.token = token; this.cancel = cancel;
            this.kind = kind; this.value = value; this.region = region; this.language = language; this.platform = platform;
        }
        @Override public void run() {
            String response;
            try { response = bridge.callAttr("run_query", kind, value, region, language, platform, cancel).toString(); }
            catch (Exception error) { response = "{\"ok\":false,\"error\":{\"code\":\"source_unavailable\"}}"; }
            String json = response;
            deliver(activity, a -> a.acceptQuery(json, token, cancel));
        }
    }

    private static final class ReportTask implements Runnable {
        final WeakReference<MainActivity> activity;
        final PyObject bridge;
        final String response, format;
        ReportTask(MainActivity activity, PyObject bridge, String response, String format) {
            this.activity = new WeakReference<>(activity); this.bridge = bridge; this.response = response; this.format = format;
        }
        @Override public void run() {
            String report;
            try { report = bridge.callAttr("render_report", response, format).toString(); }
            catch (Exception error) { report = null; }
            String value = report;
            deliver(activity, a -> a.acceptReport(value, format));
        }
    }

    private static final class SaveTask implements Runnable {
        final WeakReference<MainActivity> activity;
        final ContentResolver resolver;
        final Uri uri;
        final byte[] bytes;
        SaveTask(MainActivity activity, ContentResolver resolver, Uri uri, byte[] bytes) {
            this.activity = new WeakReference<>(activity); this.resolver = resolver; this.uri = uri; this.bytes = bytes;
        }
        @Override public void run() {
            boolean success;
            try (OutputStream output = resolver.openOutputStream(uri, "wt")) {
                if (output == null) throw new java.io.IOException("No document output");
                output.write(bytes); output.flush(); success = true;
            } catch (Exception error) { success = false; }
            boolean saved = success;
            deliver(activity, a -> a.toast(a.t(saved ? "saved" : "export_failed", saved ? "Export complete" : "Export failed")));
        }
    }

    private JSONObject toolAt(int index) {
        JSONObject tool = tools.optJSONObject(index);
        return tool == null ? new JSONObject() : tool;
    }
    private List<String> labels(JSONArray array) {
        List<String> labels = new ArrayList<>();
        for (int i = 0; i < array.length(); i++) {
            JSONObject object = array.optJSONObject(i);
            labels.add(object.optString("title", object.optString("label", object.optString("id"))));
        }
        return labels;
    }
    private List<String> languageNames() {
        JSONArray languages = config.optJSONArray("languages");
        return languages == null ? java.util.Arrays.asList("简体中文", "English", "日本語", "Español") : labels(languages);
    }
    private String t(String key, String fallback) { return ui.optString(key, fallback); }
    private String local(String zh, String en, String ja, String es) {
        return language.equals("en") ? en : language.equals("ja") ? ja : language.equals("es") ? es : zh;
    }
    private String elapsed() { return String.format(Locale.ROOT, "%.1f s", (SystemClock.elapsedRealtime() - startedAt) / 1000.0); }
    private void toast(String value) { Toast.makeText(this, value, Toast.LENGTH_SHORT).show(); }
    private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private LinearLayout column() { LinearLayout layout = new LinearLayout(this); layout.setOrientation(LinearLayout.VERTICAL); return layout; }
    private LinearLayout row() { LinearLayout layout = new LinearLayout(this); layout.setOrientation(LinearLayout.HORIZONTAL); return layout; }
    private TextView text(String value, float size, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value); view.setTextSize(size); view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
        view.setIncludeFontPadding(false);
        return view;
    }
    private TextView label(String value) {
        TextView view = text(value, 11, MUTED, true);
        view.setPadding(0, dp(8), 0, dp(8));
        return view;
    }
    private TextView kicker(String number, String title) {
        TextView view = text(number + " / " + title, 12, GREEN, true);
        view.setPadding(0, 0, 0, dp(12));
        view.setLetterSpacing(.05f);
        return view;
    }
    private LinearLayout panel() {
        LinearLayout layout = column();
        layout.setPadding(dp(16), dp(16), dp(16), dp(14));
        GradientDrawable background = new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[]{PANEL, Color.rgb(13, 23, 36)});
        background.setCornerRadius(dp(18));
        background.setStroke(dp(1), LINE);
        layout.setBackground(background);
        return layout;
    }
    private GradientDrawable round(int color, int stroke, int radius) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color); drawable.setCornerRadius(dp(radius)); drawable.setStroke(dp(1), stroke);
        return drawable;
    }
    private Button button(String title, boolean primary) {
        Button button = new Button(this);
        button.setText(title); button.setTextSize(13); button.setAllCaps(false);
        button.setTextColor(primary ? BG : GREEN);
        button.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
        button.setMinHeight(dp(48)); button.setMinimumHeight(dp(48)); button.setMinWidth(0); button.setMinimumWidth(0);
        button.setPadding(dp(12), dp(5), dp(12), dp(5));
        StateListDrawable states = new StateListDrawable();
        states.addState(new int[]{-android.R.attr.state_enabled}, round(primary ? Color.rgb(33, 64, 66) : PANEL, LINE, 10));
        GradientDrawable enabled = primary
                ? new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, new int[]{GREEN, CYAN})
                : round(INPUT, LINE, 10);
        enabled.setCornerRadius(dp(10));
        states.addState(new int[]{}, enabled);
        button.setBackground(new RippleDrawable(android.content.res.ColorStateList.valueOf(Color.argb(50, 105, 217, 204)), states, null));
        button.setBackgroundTintList(null);
        button.setElevation(primary ? dp(2) : 0);
        button.setTextColor(new android.content.res.ColorStateList(
                new int[][]{new int[]{-android.R.attr.state_enabled}, new int[]{}}, new int[]{MUTED, primary ? BG : GREEN}));
        return button;
    }
    private void weightedButton(LinearLayout row, Button button, boolean first) {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, -2, 1);
        if (first) params.rightMargin = dp(4); else params.leftMargin = dp(4);
        row.addView(button, params);
    }
    private EditText input(String hint) {
        EditText edit = new EditText(this);
        edit.setTextSize(14); edit.setTextColor(TEXT); edit.setHintTextColor(MUTED); edit.setHint(hint);
        edit.setBackground(round(INPUT, LINE, 10)); edit.setPadding(dp(13), dp(12), dp(13), dp(12));
        edit.setSelectAllOnFocus(false);
        return edit;
    }
    private Spinner spinner(List<String> values) {
        Spinner picker = new Spinner(this, Spinner.MODE_DROPDOWN);
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_item, values) {
            @Override public View getView(int position, View convertView, ViewGroup parent) {
                TextView view = (TextView) super.getView(position, convertView, parent);
                view.setTextColor(TEXT); view.setTextSize(14); view.setSingleLine(false); view.setMaxLines(2);
                view.setText(values.get(position) + "  ▾");
                view.setPadding(dp(12), dp(8), dp(24), dp(8));
                return view;
            }
            @Override public View getDropDownView(int position, View convertView, ViewGroup parent) {
                TextView view = (TextView) super.getDropDownView(position, convertView, parent);
                view.setTextColor(TEXT); view.setTextSize(14); view.setBackgroundColor(PANEL);
                view.setMinHeight(dp(48)); view.setGravity(Gravity.CENTER_VERTICAL);
                view.setPadding(dp(16), dp(10), dp(16), dp(10));
                return view;
            }
        };
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        picker.setAdapter(adapter); picker.setBackground(round(INPUT, LINE, 10));
        return picker;
    }
    private TextView metric(LinearLayout parent, String value, String caption) {
        LinearLayout card = column();
        card.setPadding(dp(11), dp(10), dp(8), dp(10));
        card.setBackground(round(PANEL, LINE, 12));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, -2, 1);
        if (parent.getChildCount() > 0) params.leftMargin = dp(8);
        parent.addView(card, params);
        TextView number = text(value, 20, GREEN, true);
        number.setTypeface(Typeface.MONOSPACE);
        card.addView(number);
        TextView label = text(caption, 9, MUTED, true);
        label.setPadding(0, dp(5), 0, 0);
        card.addView(label);
        return number;
    }
    private void applyInsets(View view) {
        final int left = view.getPaddingLeft(), top = view.getPaddingTop(), right = view.getPaddingRight(), bottom = view.getPaddingBottom();
        view.setOnApplyWindowInsetsListener((v, insets) -> {
            v.setPadding(left + insets.getSystemWindowInsetLeft(), top + insets.getSystemWindowInsetTop(),
                    right + insets.getSystemWindowInsetRight(), bottom + insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
        });
        view.requestApplyInsets();
    }
    private final class Radar extends View {
        final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        Radar(Context context) { super(context); setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO); }
        @Override protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            float cx = getWidth() / 2f, cy = getHeight() / 2f, radius = Math.min(cx, cy) - dp(10);
            paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(dp(1)); paint.setColor(LINE);
            canvas.drawCircle(cx, cy, radius, paint); canvas.drawCircle(cx, cy, radius * .62f, paint);
            canvas.drawLine(cx - radius, cy, cx + radius, cy, paint); canvas.drawLine(cx, cy - radius, cx, cy + radius, paint);
            paint.setColor(GREEN); canvas.drawArc(cx - radius, cy - radius, cx + radius, cy + radius, -90, 80, false, paint);
            paint.setStyle(Paint.Style.FILL); canvas.drawCircle(cx, cy, dp(3), paint);
        }
    }
}
